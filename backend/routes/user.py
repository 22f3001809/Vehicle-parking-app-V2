from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, User, ParkingLot, ParkingSpot, Reservation
from datetime import datetime
from functools import wraps

user_bp = Blueprint('user', __name__, url_prefix='/api/user')


def user_required():
    """Decorator to ensure only regular users (not admins) access user routes"""
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
def dashboard():
    """User dashboard - personal statistics"""
    current_user_id = get_jwt_identity()
    
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
def get_parking_lots():
    """Get all available parking lots"""
    search = request.args.get('search', '')
    
    query = ParkingLot.query.filter_by(is_active=True)
    
    # Search by name, address, or pin_code
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


@user_bp.route('/parking-lots/<int:lot_id>/book', methods=['POST'])
@jwt_required()
def book_parking_spot(lot_id):
    """Book an available parking spot in a lot (automatically allocated)"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('vehicle_number'):
        return jsonify({'error': 'Vehicle number is required'}), 400
    
    # Check if user already has an active or pending reservation
    existing = Reservation.query.filter(
        Reservation.user_id == current_user_id,
        Reservation.status.in_(['pending', 'active'])
    ).first()
    
    if existing:
        return jsonify({'error': 'You already have an active reservation'}), 400
    
    # Find first available spot in the lot (automatic allocation)
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
        vehicle_number=data['vehicle_number'],
        status='pending'
    )
    
    db.session.add(reservation)
    db.session.commit()
    
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
    
    return jsonify({
        'message': 'Checked in successfully. Vehicle parked.',
        'reservation': reservation.to_dict()
    }), 200


@user_bp.route('/reservations/<int:reservation_id>/release', methods=['POST'])
@jwt_required()
def release_spot(reservation_id):
    """Release/vacate the parking spot"""
    current_user_id = get_jwt_identity()
    
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
    
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Verify ownership
    if reservation.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if reservation.status != 'pending':
        return jsonify({'error': 'Only pending reservations can be cancelled'}), 400
    
    # Cancel reservation
    reservation.status = 'cancelled'
    
    db.session.commit()
    
    return jsonify({
        'message': 'Reservation cancelled successfully',
        'reservation': reservation.to_dict()
    }), 200
