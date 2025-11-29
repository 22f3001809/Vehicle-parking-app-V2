from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, User, ParkingLot, ParkingSpot, Reservation
from cache_config import cache
from utils.cache_utils import (
    CACHE_TIMEOUT_LOTS, 
    CACHE_TIMEOUT_SPOTS,
    CACHE_TIMEOUT_DASHBOARD,
    invalidate_lot_cache,
    invalidate_user_cache
)
from datetime import datetime
from functools import wraps
import pytz
from celery_app import celery_app

user_bp = Blueprint('user', __name__, url_prefix='/api/user')


def user_required():
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if claims.get('is_admin'):
                return jsonify({'error': 'This endpoint is for regular users only'}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper


@user_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@cache.cached(timeout=CACHE_TIMEOUT_DASHBOARD, key_prefix=lambda: f"user_dashboard_{get_jwt_identity()}")
def dashboard():
    """User dashboard - personal statistics"""
    current_user_id = get_jwt_identity()
    try:
        current_user_id = int(current_user_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid token identity'}), 401
    
    # Get user's active reservation
    active_reservation = Reservation.query.filter_by(
        user_id=current_user_id,
        status='active'
    ).first()
    
    # Get statistics
    total_reservations = Reservation.query.filter_by(user_id=current_user_id).count()
    completed_reservations = Reservation.query.filter_by(
        user_id=current_user_id, status='completed'
    ).count()
    
    # Calculate total spent
    completed = Reservation.query.filter_by(
        user_id=current_user_id, status='completed'
    ).all()
    total_spent = sum(res.parking_cost or 0 for res in completed)
    
    response = {
        'total_reservations': total_reservations,
        'completed_reservations': completed_reservations,
        'total_spent': round(total_spent, 2),
        'active_reservation': active_reservation.to_dict() if active_reservation else None
    }
    
    return jsonify(response), 200


@user_bp.route('/parking-lots', methods=['GET'])
@jwt_required()
@cache.cached(timeout=CACHE_TIMEOUT_LOTS, query_string=True)
def get_parking_lots():
    """Get all available parking lots"""
    search = request.args.get('search', '')
    
    query = ParkingLot.query.filter_by(is_active=True)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            db.or_(
                ParkingLot.name.ilike(search_pattern),
                ParkingLot.address.ilike(search_pattern),
                ParkingLot.pin_code.ilike(search_pattern),
                ParkingLot.city.ilike(search_pattern)
            )
        )
    
    lots = query.all()
    return jsonify([lot.to_dict() for lot in lots]), 200


@user_bp.route('/parking-lots/<int:lot_id>', methods=['GET'])
@jwt_required()
@cache.cached(timeout=CACHE_TIMEOUT_LOTS)
def get_parking_lot_details(lot_id):
    """Get specific parking lot details"""
    lot = ParkingLot.query.get_or_404(lot_id)
    
    if not lot.is_active:
        return jsonify({'error': 'This parking lot is not available'}), 404
    
    return jsonify(lot.to_dict()), 200

@user_bp.route('/parking-lots/<int:lot_id>/book', methods=['POST'])
@jwt_required()
def book_parking_spot(lot_id):
    """Book an available parking spot in a lot (automatically allocated)"""
    current_user_id = get_jwt_identity()
    try:
        current_user_id = int(current_user_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid token identity'}), 401
    data = request.get_json()
    
    if not data or not data.get('vehicle_number'):
        return jsonify({'error': 'Vehicle number is required'}), 400
    
    # Check if this specific vehicle already has an active reservation
    vehicle_number = data['vehicle_number'].strip().upper()
    
    vehicle_reservation = Reservation.query.filter(
        Reservation.user_id == current_user_id,
        Reservation.vehicle_number == vehicle_number,
        Reservation.status.in_(['pending', 'active'])
    ).first()
    
    if vehicle_reservation:
        return jsonify({'error': f'This vehicle ({vehicle_number}) already has an active reservation'}), 400
    
    # Find first available spot in the lot 
    spot = ParkingSpot.query.filter_by(
        lot_id=lot_id,
        status='A'
    ).order_by(ParkingSpot.spot_number).first()
    
    if not spot:
        return jsonify({'error': 'No available spots in this parking lot'}), 404
    
    # Create reservation (status: pending until check-in)
    reservation = Reservation(
        spot_id=spot.id,
        user_id=current_user_id,
        vehicle_number=vehicle_number,
        status='pending'
    )
    
    # Update spot status to Reserved
    spot.status = 'R'
    
    db.session.add(reservation)
    db.session.commit()
    
    # Refresh to get updated relationships
    db.session.refresh(reservation)
    
    # Invalidate user cache after booking
    invalidate_user_cache(current_user_id)
    
    return jsonify({
        'message': f'Spot {spot.spot_number} reserved successfully',
        'reservation': reservation.to_dict(),
        'spot': spot.to_dict()
    }), 201


@user_bp.route('/reservations/<int:reservation_id>/checkin', methods=['POST'])
@jwt_required()
def checkin_reservation(reservation_id):
    """Check in - mark vehicle as parked (change spot status to Occupied)"""
    current_user_id = get_jwt_identity()
    try:
        current_user_id = int(current_user_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid token identity'}), 401
    
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Verify ownership
    if reservation.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if reservation.status != 'pending':
        return jsonify({'error': 'Reservation is not in pending state'}), 400
    
    if not reservation.parking_spot:
        return jsonify({'error': 'Parking spot not found'}), 404
    
    # Update reservation and spot status
    reservation.status = 'active'
    reservation.check_in_timestamp = datetime.utcnow()
    reservation.parking_spot.status = 'O'  # Occupied
    
    db.session.commit()
    
    # Invalidate user cache after check-in
    invalidate_user_cache(current_user_id)
    
    return jsonify({
        'message': 'Checked in successfully. Vehicle parked.',
        'reservation': reservation.to_dict()
    }), 200


@user_bp.route('/reservations/<int:reservation_id>/release', methods=['POST'])
@jwt_required()
def release_spot(reservation_id):
    """Release/vacate the parking spot"""
    current_user_id = get_jwt_identity()
    try:
        current_user_id = int(current_user_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid token identity'}), 401
    
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Verify ownership
    if reservation.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if reservation.status != 'active':
        return jsonify({'error': 'Reservation is not active'}), 400
    
    if not reservation.parking_spot:
        return jsonify({'error': 'Parking spot not found'}), 404
    
    # Calculate cost and release spot
    reservation.check_out_timestamp = datetime.utcnow()
    reservation.parking_cost = reservation.calculate_cost()
    reservation.status = 'completed'
    reservation.parking_spot.status = 'A'  # Available
    
    db.session.commit()
    
    # Invalidate user cache after checkout
    invalidate_user_cache(current_user_id)
    
    return jsonify({
        'message': 'Spot released successfully',
        'reservation': reservation.to_dict(),
        'cost': reservation.parking_cost
    }), 200


@user_bp.route('/reservations', methods=['GET'])
@jwt_required()
def get_my_reservations():
    """Get current user's reservation history"""
    current_user_id = get_jwt_identity()
    try:
        current_user_id = int(current_user_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid token identity'}), 401
    
    status = request.args.get('status')  # Filter by status
    
    query = Reservation.query.filter_by(user_id=current_user_id)
    if status:
        query = query.filter_by(status=status)
    
    reservations = query.order_by(Reservation.booking_timestamp.desc()).all()
    
    return jsonify([res.to_dict() for res in reservations]), 200


@user_bp.route('/reservations/<int:reservation_id>', methods=['GET'])
@jwt_required()
def get_reservation_details(reservation_id):
    """Get specific reservation details"""
    current_user_id = get_jwt_identity()
    try:
        current_user_id = int(current_user_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid token identity'}), 401
    
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Verify ownership
    if reservation.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    result = reservation.to_dict()
    
    # Add parking spot and lot details
    if reservation.parking_spot:
        result['spot'] = reservation.parking_spot.to_dict()
        if reservation.parking_spot.parking_lot:
            result['parking_lot'] = reservation.parking_spot.parking_lot.to_dict()
    
    return jsonify(result), 200


@user_bp.route('/reservations/<int:reservation_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_reservation(reservation_id):
    """Cancel a pending reservation"""
    current_user_id = get_jwt_identity()
    try:
        current_user_id = int(current_user_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid token identity'}), 401
    
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Verify ownership
    if reservation.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if reservation.status != 'pending':
        return jsonify({'error': 'Only pending reservations can be cancelled'}), 400
    
    # Cancel reservation and free up the spot
    reservation.status = 'cancelled'
    
    # If spot was reserved, make it available again
    if reservation.parking_spot and reservation.parking_spot.status == 'R':
        reservation.parking_spot.status = 'A'
    
    db.session.commit()
    
    return jsonify({
        'message': 'Reservation cancelled successfully',
        'reservation': reservation.to_dict()
    }), 200


@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    current_user_id = get_jwt_identity()
    try:
        current_user_id = int(current_user_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid token identity'}), 401
    
    user = User.query.get_or_404(current_user_id)
    return jsonify({'user': user.to_dict()}), 200


@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    current_user_id = get_jwt_identity()
    try:
        current_user_id = int(current_user_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid token identity'}), 401
    
    user = User.query.get_or_404(current_user_id)
    data = request.get_json()
    
    # Update allowed fields
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'email' in data:
        # Check if email is already taken by another user
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != current_user_id:
            return jsonify({'error': 'Email already in use'}), 400
        user.email = data['email']
    if 'phone_number' in data:
        user.phone_number = data['phone_number']
    if 'address' in data:
        user.address = data['address']
    if 'pincode' in data:
        user.pin_code = data['pincode']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': user.to_dict()
    }), 200


@user_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    current_user_id = get_jwt_identity()
    try:
        current_user_id = int(current_user_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid token identity'}), 401
    
    user = User.query.get_or_404(current_user_id)
    data = request.get_json()
    
    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Verify current password
    if not user.check_password(data['current_password']):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    # Update password
    user.set_password(data['new_password'])
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'}), 200


@user_bp.route('/reservations/<int:reservation_id>/checkout-details', methods=['GET'])
@jwt_required()
def get_checkout_details(reservation_id):
    """Get checkout details (cost, duration) without performing checkout"""
    current_user_id = get_jwt_identity()
    try:
        current_user_id = int(current_user_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid token identity'}), 401

    reservation = Reservation.query.get_or_404(reservation_id)

    if reservation.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    if reservation.status != 'active':
        return jsonify({'error': 'Reservation is not active'}), 400

    if not reservation.check_in_timestamp:
        return jsonify({'error': 'Cannot calculate cost before check-in'}), 400

    # Simulate checkout to calculate cost
    simulated_check_out_time = datetime.utcnow()
    duration = simulated_check_out_time - reservation.check_in_timestamp
    duration_hours = duration.total_seconds() / 3600.0
    charged_hours = max(1.0, duration_hours)
    
    cost = 0
    if reservation.parking_spot and reservation.parking_spot.parking_lot:
        cost = charged_hours * reservation.parking_spot.parking_lot.price_per_hour

    duration_str = ""
    hours = int(duration.total_seconds() // 3600)
    minutes = int((duration.total_seconds() % 3600) // 60)
    if hours > 0:
        duration_str = f"{hours}h {minutes}m"
    else:
        duration_str = f"{minutes}m"

    return jsonify({
        'spot_id': reservation.parking_spot.spot_number if reservation.parking_spot else 'N/A',
        'vehicle_number': reservation.vehicle_number,
        'check_in_time': reservation.check_in_timestamp.strftime('%Y-%m-%d %H:%M:%S') if reservation.check_in_timestamp else 'N/A',
        'check_out_time': simulated_check_out_time.strftime('%Y-%m-%d %H:%M:%S'),
        'duration': duration_str,
        'cost': round(cost, 2)
    }), 200


@user_bp.route('/export-csv', methods=['POST'])
@jwt_required()
def trigger_csv_export():
    """
    Trigger CSV export of user's parking history
    """
    current_user_id = get_jwt_identity()
    try:
        current_user_id = int(current_user_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid token identity'}), 401
    
    # Verify user exists
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        task = celery_app.send_task('tasks.csv_export', args=[current_user_id])
        
        return jsonify({
            'status': 'processing',
            'message': 'CSV export started. You will receive an email shortly.',
            'task_id': task.id
        }), 202
    except Exception as e:
        print(f"[ERROR] Failed to start task: {e}")
        return jsonify({
            'error': 'Failed to start CSV export',
            'details': str(e)
        }), 500


@user_bp.route('/export-status/<task_id>', methods=['GET'])
@jwt_required()
def get_export_status(task_id):
    """
    Check status of CSV export task
    """
    try:
        # We use the app instance to look up the result
        task = celery_app.AsyncResult(task_id)
        
        # .state, .status, and .result are the standard attributes
        state = task.state
        
        response = {
            'status': state,
            'task_id': task_id
        }

        if state == 'PENDING':
            # PENDING means the task is waiting in the queue OR the ID is unknown
            response['message'] = 'Task is waiting in queue...'
            response['status'] = 'pending'
            
        elif state == 'STARTED' or state == 'PROGRESS':
            response['status'] = 'processing'
            # If you set custom state in the task using update_state, it appears in task.info
            info = task.info if isinstance(task.info, dict) else {}
            response['message'] = info.get('message', 'Processing export...')
            
        elif state == 'SUCCESS':
            response['status'] = 'success'
            # task.result contains the return value of the function (the dict we returned in the task)
            result = task.result if isinstance(task.result, dict) else {}
            response['message'] = 'Export completed! Check your email.'
            response['filename'] = result.get('filename')
            
        elif state == 'FAILURE':
            response['status'] = 'error'
            response['message'] = 'Export failed.'
            # task.result would be the exception object here
            response['error_details'] = str(task.result)
            
        return jsonify(response), 200
        
    except Exception as e:
        print(f"[ERROR] Export status check failed: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to check status'}), 500