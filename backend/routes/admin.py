from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, User, ParkingLot, ParkingSpot, Reservation
from functools import wraps

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
    available_spots = ParkingSpot.query.filter_by(status='A').count()
    total_users = User.query.filter_by(is_admin=False).count()
    
    active_reservations = Reservation.query.filter_by(status='active').count()
    completed_reservations = Reservation.query.filter_by(status='completed').count()
    
    return jsonify({
        'total_lots': total_lots,
        'total_spots': total_spots,
        'occupied_spots': occupied_spots,
        'available_spots': available_spots,
        'total_users': total_users,
        'active_reservations': active_reservations,
        'completed_reservations': completed_reservations
    }), 200


@admin_bp.route('/parking-lots', methods=['GET'])
@admin_required()
def get_all_parking_lots():
    """Get all parking lots with details"""
    lots = ParkingLot.query.all()
    return jsonify([lot.to_dict() for lot in lots]), 200


@admin_bp.route('/parking-lots', methods=['POST'])
@admin_required()
def create_parking_lot():
    """Create a new parking lot with spots"""
    data = request.get_json()
    
    # Validate input
    required_fields = ['name', 'address', 'pin_code', 'price_per_hour', 'number_of_spots']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if lot name already exists
    if ParkingLot.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Parking lot with this name already exists'}), 400
    
    # Create parking lot
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
    db.session.flush()  # Get lot.id before creating spots
    
    # Auto-create parking spots
    for i in range(1, data['number_of_spots'] + 1):
        spot = ParkingSpot(
            spot_number=f"S{i:03d}",  # S001, S002, etc.
            lot_id=lot.id,
            status='A'  # Available
        )
        db.session.add(spot)
    
    db.session.commit()
    
    return jsonify({
        'message': f'Parking lot created with {data["number_of_spots"]} spots',
        'parking_lot': lot.to_dict()
    }), 201


@admin_bp.route('/parking-lots/<int:lot_id>', methods=['PUT'])
@admin_required()
def update_parking_lot(lot_id):
    """Update parking lot details"""
    lot = ParkingLot.query.get_or_404(lot_id)
    data = request.get_json()
    
    # Update fields
    if 'name' in data:
        # Check if new name is taken by another lot
        existing = ParkingLot.query.filter_by(name=data['name']).first()
        if existing and existing.id != lot_id:
            return jsonify({'error': 'Parking lot name already exists'}), 400
        lot.name = data['name']
    
    if 'address' in data:
        lot.address = data['address']
    if 'pin_code' in data:
        lot.pin_code = data['pin_code']
    if 'price_per_hour' in data:
        lot.price_per_hour = data['price_per_hour']
    if 'city' in data:
        lot.city = data['city']
    if 'state' in data:
        lot.state = data['state']
    if 'is_active' in data:
        lot.is_active = data['is_active']
    
    # Handle spot increase/decrease
    if 'number_of_spots' in data:
        current_spots = lot.number_of_spots
        new_spots = data['number_of_spots']
        
        if new_spots > current_spots:
            # Add new spots
            for i in range(current_spots + 1, new_spots + 1):
                spot = ParkingSpot(
                    spot_number=f"S{i:03d}",
                    lot_id=lot.id,
                    status='A'
                )
                db.session.add(spot)
            lot.number_of_spots = new_spots
        elif new_spots < current_spots:
            # Can only delete available spots
            spots_to_delete = current_spots - new_spots
            available_spots = ParkingSpot.query.filter_by(
                lot_id=lot_id, status='A'
            ).order_by(ParkingSpot.id.desc()).limit(spots_to_delete).all()
            
            if len(available_spots) < spots_to_delete:
                return jsonify({'error': 'Cannot delete occupied spots'}), 400
            
            for spot in available_spots:
                db.session.delete(spot)
            lot.number_of_spots = new_spots
    
    db.session.commit()
    
    return jsonify({
        'message': 'Parking lot updated successfully',
        'parking_lot': lot.to_dict()
    }), 200


@admin_bp.route('/parking-lots/<int:lot_id>', methods=['DELETE'])
@admin_required()
def delete_parking_lot(lot_id):
    """Delete parking lot (only if all spots are available)"""
    lot = ParkingLot.query.get_or_404(lot_id)
    
    # Check if any spot is occupied
    occupied_spots = ParkingSpot.query.filter_by(lot_id=lot_id, status='O').count()
    if occupied_spots > 0:
        return jsonify({'error': 'Cannot delete parking lot with occupied spots'}), 400
    
    db.session.delete(lot)
    db.session.commit()
    
    return jsonify({'message': 'Parking lot deleted successfully'}), 200


@admin_bp.route('/parking-lots/<int:lot_id>/spots', methods=['GET'])
@admin_required()
def get_lot_spots(lot_id):
    """Get all spots in a parking lot"""
    lot = ParkingLot.query.get_or_404(lot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    
    result = []
    for spot in spots:
        spot_data = spot.to_dict()
        # Add current reservation info if occupied
        if spot.status == 'O':
            reservation = spot.get_current_reservation()
            if reservation:
                spot_data['current_reservation'] = {
                    'id': reservation.id,
                    'user': reservation.user.username if reservation.user else None,
                    'vehicle_number': reservation.vehicle_number,
                    'check_in_time': reservation.check_in_timestamp.isoformat() if reservation.check_in_timestamp else None
                }
        result.append(spot_data)
    
    return jsonify({
        'lot': lot.to_dict(),
        'spots': result
    }), 200


@admin_bp.route('/users', methods=['GET'])
@admin_required()
def get_all_users():
    """Get all registered users"""
    users = User.query.filter_by(is_admin=False).all()
    return jsonify([user.to_dict() for user in users]), 200


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required()
def get_user_details(user_id):
    """Get user details with reservation history"""
    user = User.query.get_or_404(user_id)
    
    if user.is_admin:
        return jsonify({'error': 'Cannot view admin details'}), 403
    
    reservations = Reservation.query.filter_by(user_id=user_id).order_by(
        Reservation.booking_timestamp.desc()
    ).all()
    
    return jsonify({
        'user': user.to_dict(),
        'reservations': [res.to_dict() for res in reservations]
    }), 200


@admin_bp.route('/reservations', methods=['GET'])
@admin_required()
def get_all_reservations():
    """Get all reservations"""
    status = request.args.get('status')  # Filter by status
    
    query = Reservation.query
    if status:
        query = query.filter_by(status=status)
    
    reservations = query.order_by(Reservation.booking_timestamp.desc()).all()
    return jsonify([res.to_dict() for res in reservations]), 200
