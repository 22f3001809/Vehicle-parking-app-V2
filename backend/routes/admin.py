from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, User, ParkingLot, ParkingSpot, Reservation
from utils.cache_utils import (
    invalidate_lot_cache,
    invalidate_all_lots_cache,
    invalidate_admin_dashboard_cache
)
from functools import wraps
import pytz
from datetime import datetime, timedelta
from sqlalchemy import func
from celery_app import celery_app

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def admin_required():
    """Decorator to check if user is admin"""
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if not claims.get('is_admin'):
                return jsonify({'error': 'Admin access required'}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper


@admin_bp.route('/dashboard', methods=['GET'])
@admin_required()
def dashboard():
    """Admin dashboard - summary statistics"""
    total_lots = ParkingLot.query.count()
    total_spots = ParkingSpot.query.count()
    occupied_spots = ParkingSpot.query.filter_by(status='O').count()
    reserved_spots = ParkingSpot.query.filter_by(status='R').count()
    available_spots = ParkingSpot.query.filter_by(status='A').count()
    total_users = User.query.filter_by(is_admin=False).count()
    
    active_reservations = Reservation.query.filter_by(status='active').count()
    pending_reservations = Reservation.query.filter_by(status='pending').count()
    completed_reservations = Reservation.query.filter_by(status='completed').count()
    
    # Calculate total revenue
    completed = Reservation.query.filter_by(status='completed').all()
    total_revenue = sum(res.parking_cost or 0 for res in completed)
    
    # recent parking lots
    recent_lots = ParkingLot.query.order_by(ParkingLot.created_at.desc()).limit(5).all()
    
    # recent users
    recent_users = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).limit(5).all()
    
    return jsonify({
        'total_lots': total_lots,
        'total_spots': total_spots,
        'occupied_spots': occupied_spots,
        'reserved_spots': reserved_spots,
        'available_spots': available_spots,
        'total_users': total_users,
        'active_reservations': active_reservations,
        'pending_reservations': pending_reservations,
        'completed_reservations': completed_reservations,
        'total_revenue': round(total_revenue, 2),
        'recent_lots': [lot.to_dict() for lot in recent_lots],
        'recent_users': [user.to_dict() for user in recent_users]
    }), 200


@admin_bp.route('/dashboard/daily-summary', methods=['GET'])
@admin_required()
def daily_summary():
    """Get daily revenue and bookings for last 7 days"""
    ist = pytz.timezone('Asia/Kolkata')
    today = datetime.now(ist).replace(hour=0, minute=0, second=0, microsecond=0)
    seven_days_ago = today - timedelta(days=6)
    
    daily_data = []
    
    for i in range(7):
        day_date = seven_days_ago + timedelta(days=i)
        day_start = day_date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        day_start_utc = day_start.astimezone(pytz.utc).replace(tzinfo=None)
        day_end_utc = day_end.astimezone(pytz.utc).replace(tzinfo=None)
        
        completed_reservations = Reservation.query.filter(
            Reservation.status == 'completed',
            Reservation.check_out_timestamp >= day_start_utc,
            Reservation.check_out_timestamp <= day_end_utc
        ).all()
        
        daily_revenue = sum(res.parking_cost or 0 for res in completed_reservations)
        daily_bookings = len(completed_reservations)
        
        daily_data.append({
            'date': day_date.strftime('%b %d'),
            'revenue': round(daily_revenue, 2),
            'bookings': daily_bookings
        })
    
    pending_count = Reservation.query.filter_by(status='pending').count()
    active_count = Reservation.query.filter_by(status='active').count()
    completed_count = Reservation.query.filter_by(status='completed').count()
    cancelled_count = Reservation.query.filter_by(status='cancelled').count()
    
    return jsonify({
        'daily_data': daily_data,
        'reservation_status': {
            'pending': pending_count,
            'active': active_count,
            'completed': completed_count,
            'cancelled': cancelled_count
        }
    }), 200


@admin_bp.route('/parking-lots', methods=['GET'])
@admin_required()
def get_all_parking_lots():
    """Get all parking lots with details"""
    lots = ParkingLot.query.all()
    return jsonify([lot.to_dict() for lot in lots]), 200


@admin_bp.route('/parking-lots', methods=['POST'])
@jwt_required()
def create_parking_lot():
    """Create a new parking lot with spots"""
    data = request.get_json()
    
    required_fields = ['name', 'address', 'pin_code', 'price_per_hour', 'number_of_spots']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if ParkingLot.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Parking lot with this name already exists'}), 400
    
    try:
        lot = ParkingLot(
            name=data['name'],
            address=data['address'],
            pin_code=data['pin_code'],
            price_per_hour=data['price_per_hour'],
            number_of_spots=data['number_of_spots'],
            city=data.get('city'),
            state=data.get('state')
        )
        
        db.session.add(lot)
        db.session.flush()
        
        for i in range(1, data['number_of_spots'] + 1):
            spot = ParkingSpot(
                spot_number=f"S{i:03d}", 
                lot_id=lot.id,
                status='A'  
            )
            db.session.add(spot)
        
        db.session.commit()
    
        try:
            invalidate_all_lots_cache()
            invalidate_admin_dashboard_cache()
        except Exception as e:
            print(f"Cache invalidation error: {e}")

        # Trigger Notification
        try:
            celery_app.send_task('tasks.notify_new_parking_lot', args=[lot.id])
            print(f"[ADMIN] Triggered GChat notification for Lot {lot.id}")
        except Exception as e:
            print(f"[ADMIN] Failed to trigger notification task: {e}")

        return jsonify({
            'message': f'Parking lot created with {data["number_of_spots"]} spots',
            'parking_lot': lot.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Failed to create parking lot: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@admin_bp.route('/parking-lots/<int:lot_id>', methods=['PUT'])
@admin_required()
def update_parking_lot(lot_id):
    """Update parking lot details"""
    lot = ParkingLot.query.get_or_404(lot_id)
    data = request.get_json()
    
    try:
        if 'name' in data:
            existing = ParkingLot.query.filter_by(name=data['name']).first()
            if existing and existing.id != lot_id:
                return jsonify({'error': 'Parking lot name already exists'}), 400
            lot.name = data['name']
        
        if 'address' in data: lot.address = data['address']
        if 'pin_code' in data: lot.pin_code = data['pin_code']
        if 'price_per_hour' in data: lot.price_per_hour = data['price_per_hour']
        if 'city' in data: lot.city = data['city']
        if 'state' in data: lot.state = data['state']
        if 'is_active' in data: lot.is_active = data['is_active']
        
        if 'number_of_spots' in data:
            current_spots = lot.number_of_spots
            new_spots = int(data['number_of_spots'])
            
            if new_spots > current_spots:
                for i in range(current_spots + 1, new_spots + 1):
                    spot = ParkingSpot(
                        spot_number=f"S{i:03d}",
                        lot_id=lot.id,
                        status='A'
                    )
                    db.session.add(spot)
                lot.number_of_spots = new_spots
                
            elif new_spots < current_spots:
                # We can only remove spots if they are Available and at the end of the list preferably
                spots_to_delete = current_spots - new_spots
                
                # Finding available spots to delete 
                available_spots = ParkingSpot.query.filter_by(
                    lot_id=lot_id, status='A'
                ).order_by(ParkingSpot.id.desc()).limit(spots_to_delete).all()
                
                if len(available_spots) < spots_to_delete:
                    # Not enough available spots to delete
                    return jsonify({
                        'error': f'Cannot reduce to {new_spots}. Some spots are occupied or reserved.'
                    }), 400
                
                for spot in available_spots:
                    db.session.delete(spot)
                lot.number_of_spots = new_spots
        
        db.session.commit()
        
        # Invalidate User Caches
        try:
            invalidate_lot_cache(lot_id)
            invalidate_all_lots_cache()
            invalidate_admin_dashboard_cache()
        except Exception:
            pass
        
        return jsonify({
            'message': 'Parking lot updated successfully',
            'parking_lot': lot.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/parking-lots/<int:lot_id>', methods=['DELETE'])
@admin_required()
def delete_parking_lot(lot_id):
    """Delete parking lot (only if all spots are available)"""
    lot = ParkingLot.query.get_or_404(lot_id)
    
    # Check for physical occupancy
    non_available_spots = ParkingSpot.query.filter(
        ParkingSpot.lot_id == lot_id,
        ParkingSpot.status != 'A'
    ).count()
    
    if non_available_spots > 0:
        return jsonify({'error': 'Cannot delete: Some spots are Occupied or Reserved.'}), 400
    
    # Checking for upcoming reservations (Pending/Active)
    active_reservations = Reservation.query.join(ParkingSpot).filter(
        ParkingSpot.lot_id == lot_id,
        Reservation.status.in_(['active', 'pending'])
    ).count()
    
    if active_reservations > 0:
        return jsonify({'error': 'Cannot delete: Active or Pending reservations exist.'}), 400
    
    try:
        db.session.delete(lot)
        db.session.commit()
        
        # Invalidate User Caches
        try:
            invalidate_lot_cache(lot_id)
            invalidate_all_lots_cache()
            invalidate_admin_dashboard_cache()
        except Exception:
            pass
        
        return jsonify({'message': 'Parking lot deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/parking-lots/<int:lot_id>/spots', methods=['GET'])
@admin_required()
def get_lot_spots(lot_id):
    """Get all spots in a parking lot"""
    lot = ParkingLot.query.get_or_404(lot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    
    result = []
    ist = pytz.timezone('Asia/Kolkata')

    for spot in spots:
        spot_data = spot.to_dict()
        
        if spot.status in ['O', 'R']:
            reservation = Reservation.query.filter(
                Reservation.spot_id == spot.id,
                Reservation.status.in_(['active', 'pending'])
            ).order_by(Reservation.booking_timestamp.desc()).first()

            if reservation:
                spot_data['current_reservation'] = {
                    'id': reservation.id,
                    'user': reservation.user.username if reservation.user else 'Unknown',
                    'vehicle_number': reservation.vehicle_number,
                    'check_in_time': pytz.utc.localize(reservation.check_in_timestamp).astimezone(ist).isoformat() if reservation.check_in_timestamp else None,
                    'booking_time': pytz.utc.localize(reservation.booking_timestamp).astimezone(ist).isoformat() if reservation.booking_timestamp else None,
                    'status': reservation.status
                }
        result.append(spot_data)
    
    return jsonify({
        'lot': lot.to_dict(),
        'spots': result
    }), 200

@admin_bp.route('/users', methods=['GET'])
@admin_required()
def get_all_users():
    users = User.query.filter_by(is_admin=False).all()
    users_data = []
    for user in users:
        user_dict = user.to_dict()
        user_dict['reservation_count'] = Reservation.query.filter_by(user_id=user.id).count()
        users_data.append(user_dict)
    return jsonify(users_data), 200

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required()
def get_user_details(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin: return jsonify({'error': 'Cannot view admin details'}), 403
    reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.booking_timestamp.desc()).all()
    return jsonify({'user': user.to_dict(), 'reservations': [res.to_dict() for res in reservations]}), 200

@admin_bp.route('/reservations', methods=['GET'])
@admin_required()
def get_all_reservations():
    status = request.args.get('status')
    query = Reservation.query
    if status: query = query.filter_by(status=status)
    reservations = query.order_by(Reservation.booking_timestamp.desc()).all()
    return jsonify([res.to_dict() for res in reservations]), 200

@admin_bp.route('/spots/<int:spot_id>/history', methods=['GET'])
@admin_required()
def get_spot_history(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)
    reservations = Reservation.query.filter_by(spot_id=spot_id).order_by(Reservation.booking_timestamp.desc()).all()
    history = []
    for res in reservations:
        res_data = res.to_dict()
        if res.user:
            res_data['user_details'] = {'id': res.user.id, 'username': res.user.username, 'email': res.user.email}
        history.append(res_data)
    return jsonify({'spot': spot.to_dict(), 'history': history}), 200