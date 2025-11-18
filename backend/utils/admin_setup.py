import os
from models import User, db


def create_admin_user():
    admin_exists = User.query.filter_by(is_admin=True).first()
    
    if not admin_exists:
        admin_username = os.environ.get('ADMIN_USERNAME')
        admin_password = os.environ.get('ADMIN_PASSWORD')
        admin_email = os.environ.get('ADMIN_EMAIL')
        
        if not admin_username or not admin_password or not admin_email:
            raise ValueError(
                "Admin credentials not found! "
                "Please set ADMIN_USERNAME, ADMIN_PASSWORD, and ADMIN_EMAIL in .env file"
            )
        
        admin = User(
            username=admin_username,
            full_name='System Administrator',
            email=admin_email,
            is_admin=True,
            is_active=True
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully")
        print(f"   Username: {admin_username}")
        print(f"   Email: {admin_email}")
    else:
        print("Admin user already exists")