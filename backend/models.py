from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """User model for both Admin and regular Users"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationship
    reservations = db.relationship('Reservation', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Return user data as dictionary (exclude password_hash)"""
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
            'phone_number': self.phone_number,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


class ParkingLot(db.Model):
    __tablename__ = 'parking_lots'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    address = db.Column(db.String(255), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False, index=True)
    price_per_hour = db.Column(db.Float, nullable=False)  
    number_of_spots = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional attributes
    city = db.Column(db.String(64), nullable=True, index=True)
    state = db.Column(db.String(64), nullable=True)
    
    # Relationships
    spots = db.relationship('ParkingSpot', back_populates='parking_lot', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_available_spots_count(self):
        return self.spots.filter_by(status='A').count()
    
    def get_occupied_spots_count(self):
        return self.spots.filter_by(status='O').count()
    
    def get_reserved_spots_count(self):
        return self.spots.filter_by(status='R').count()
    
    def to_dict(self):
        """Return parking lot data as dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'pin_code': self.pin_code,
            'price_per_hour': self.price_per_hour,
            'number_of_spots': self.number_of_spots,
            'available_spots': self.get_available_spots_count(),
            'occupied_spots': self.get_occupied_spots_count(),
            'reserved_spots': self.get_reserved_spots_count(),
            'is_active': self.is_active,
            'city': self.city,
            'state': self.state,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ParkingLot {self.name}>'


class ParkingSpot(db.Model):
    __tablename__ = 'parking_spots'
    
    id = db.Column(db.Integer, primary_key=True)
    spot_number = db.Column(db.String(20), nullable=False) 
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id', ondelete='CASCADE'), nullable=False, index=True)
    status = db.Column(db.String(1), default='A', nullable=False)  # 'A' = Available, 'O' = Occupied
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # spot_number must be unique within a lot
    __table_args__ = (
        db.UniqueConstraint('lot_id', 'spot_number', name='_lot_spot_uc'),
        db.Index('idx_lot_status', 'lot_id', 'status'),
    )
    
    # Relationships
    parking_lot = db.relationship('ParkingLot', back_populates='spots')
    reservations = db.relationship('Reservation', back_populates='parking_spot', lazy='dynamic')
    
    def get_current_reservation(self):
        return self.reservations.filter_by(status='active').first()
    
    def to_dict(self):
        """Return parking spot data as dictionary"""
        return {
            'id': self.id,
            'spot_number': self.spot_number,
            'lot_id': self.lot_id,
            'status': self.status,
            'status_display': 'Available' if self.status == 'A' else 'Occupied',
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ParkingSpot {self.spot_number} in Lot {self.lot_id} - Status: {self.status}>'


class Reservation(db.Model):
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id', ondelete='SET NULL'), nullable=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    vehicle_number = db.Column(db.String(20), nullable=False)
    
    booking_timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    check_in_timestamp = db.Column(db.DateTime, nullable=True)
    check_out_timestamp = db.Column(db.DateTime, nullable=True)
  
    parking_cost = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, active, completed, cancelled
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_user_status', 'user_id', 'status'),
        db.Index('idx_spot_status', 'spot_id', 'status'),
        db.Index('idx_booking_timestamp', 'booking_timestamp')
    )
    
    # Relationships
    parking_spot = db.relationship('ParkingSpot', back_populates='reservations')
    user = db.relationship('User', back_populates='reservations')
    
    def calculate_cost(self):
        """Calculate parking cost based on duration and lot price"""
        if not self.check_out_timestamp or not self.parking_spot or not self.parking_spot.parking_lot:
            return 0.0
        
        duration = self.check_out_timestamp - self.check_in_timestamp if self.check_in_timestamp else self.check_out_timestamp - self.booking_timestamp
        duration_hours = duration.total_seconds() / 3600.0
        
        # Minimum charge for 1 hour
        charged_hours = max(1.0, duration_hours)
        cost = charged_hours * self.parking_spot.parking_lot.price_per_hour
        return round(cost, 2)
    
    def get_duration_string(self):
        """Get human-readable duration string"""
        if not self.check_out_timestamp:
            start_time = self.check_in_timestamp if self.check_in_timestamp else self.booking_timestamp
            duration = datetime.utcnow() - start_time
        else:
            start_time = self.check_in_timestamp if self.check_in_timestamp else self.booking_timestamp
            duration = self.check_out_timestamp - start_time
        
        hours = int(duration.total_seconds() // 3600)
        minutes = int((duration.total_seconds() % 3600) // 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def to_dict(self):
        """Return reservation data as dictionary"""
        lot_name = None
        spot_number = None
        if self.parking_spot:
            spot_number = self.parking_spot.spot_number
            if self.parking_spot.parking_lot:
                lot_name = self.parking_spot.parking_lot.name

        result = {
            'id': self.id,
            'spot_id': self.spot_id,
            'user_id': self.user_id,
            'vehicle_number': self.vehicle_number,
            'booking_timestamp': self.booking_timestamp.isoformat() if self.booking_timestamp else None,
            'check_in_timestamp': self.check_in_timestamp.isoformat() if self.check_in_timestamp else None,
            'check_out_timestamp': self.check_out_timestamp.isoformat() if self.check_out_timestamp else None,
            'parking_cost': self.parking_cost,
            'status': self.status,
            'duration': self.get_duration_string() if self.check_in_timestamp or self.check_out_timestamp else None,
            'lot_name': lot_name,
            'spot_number': spot_number
        }
        
        # Include user details if user exists
        if self.user:
            result['username'] = self.user.username
            result['user_email'] = self.user.email
        
        return result
    
    def __repr__(self):
        spot_info = self.parking_spot.spot_number if self.parking_spot else f"Deleted Spot (ID: {self.spot_id})"
        user_info = self.user.username if self.user else f"User ID: {self.user_id}"
        return f'<Reservation {self.id} | Spot: {spot_info} | User: {user_info} | Status: {self.status}>'


