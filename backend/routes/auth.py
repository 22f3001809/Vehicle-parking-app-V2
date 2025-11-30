from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User
from celery_app import celery_app 

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create new user
    user = User(
        username=data['username'],
        full_name=data.get('full_name', data['username']),
        email=data['email'],
        phone_number=data.get('phone_number'),
        address=data.get('address'),
        pin_code=data.get('pin_code'),
        is_admin=False
    )
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        
        celery_app.send_task('tasks.notify_new_user', args=[user.id])
        
        print(f"[AUTH] Queued GChat notification for user {user.id}")

        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"[AUTH] Registration failed: {e}")
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user/admin and return JWT token"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
    
    # Find user
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    # Update last login
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Create JWT token
    additional_claims = {
        'is_admin': user.is_admin,
        'username': user.username
    }
    access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
    
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict(),
        'redirect': '/admin/dashboard' if user.is_admin else '/user/dashboard'
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info from token"""
    current_user_id = get_jwt_identity()
    try:
        user_id = int(current_user_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid token identity'}), 401
        
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()}), 200