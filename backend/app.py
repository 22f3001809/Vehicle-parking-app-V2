from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

load_dotenv()

from models import db
from config import config
from utils.admin_setup import create_admin_user
from cache_config import init_cache


def create_app(config_name='default'):
    app = Flask(__name__)
    
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    CORS(app) 
    jwt = JWTManager(app)
    migrate = Migrate(app, db)
    init_cache(app)
    
    # Register Bps
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.user import user_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    
    with app.app_context():
        db.create_all()
        create_admin_user()
    
    @app.route('/')
    def index():
        """API root endpoint"""
        return jsonify({
            'message': 'Vehicle Parking App API V2',
            'version': '2.0',
            'endpoints': {
                'auth': '/api/auth',
                'admin': '/api/admin',
                'user': '/api/user'
            }
        }), 200
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    return app


if __name__ == "__main__":
    env = os.environ.get('FLASK_ENV', 'development')
    app = create_app(config_name=env)
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)