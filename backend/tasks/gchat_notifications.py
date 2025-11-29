from celery import shared_task
from models import db, User, ParkingLot
import requests
import os

print("[TASK] Google Chat notifications module loaded")

def get_app():
    try:
        from celery_app import _app
        if _app: return _app
        from app import create_app
        return create_app()
    except ImportError:
        from app import create_app
        return create_app()

def send_gchat_notification(message):
    webhook_url = os.environ.get('GOOGLE_CHAT_WEBHOOK_URL')
    if not webhook_url: return {'status': 'error', 'message': 'No URL'}
    
    try:
        # Set a timeout so it doesn't hang forever
        requests.post(webhook_url, json={"text": message}, timeout=5)
        print(f"[GCHAT]  Message sent")
        return {'status': 'success'}
    except Exception as e:
        print(f"[GCHAT]  Error: {e}")
        return {'status': 'error'}
    
@shared_task(name='tasks.notify_new_user', bind=True, max_retries=10, default_retry_delay=0.5)
def notify_new_user(self, user_id):
    try:
        app = get_app()
        with app.app_context():
            user = User.query.get(user_id)
            
            if not user:
                print(f"[RETRY] User {user_id} not found. Retrying in 0.5s...")
                raise self.retry(exc=Exception("User not visible"))
            
            message = (
                f"*Welcome, {user.full_name}!* \n\n"
                f"Please go ahead and *book your first parking spot* now!\n"
            )
            return send_gchat_notification(message)
    except Exception as e:
        if "User not visible" in str(e): raise e
        print(f"[ERROR] {e}")

@shared_task(name='tasks.notify_new_parking_lot', bind=True, max_retries=10, default_retry_delay=0.5)
def notify_new_parking_lot(self, lot_id):
    try:
        app = get_app()
        with app.app_context():
            lot = ParkingLot.query.get(lot_id)
            
            if not lot:
                print(f"[RETRY] Lot {lot_id} not found. Retrying in 0.5s...")
                raise self.retry(exc=Exception("Lot not visible"))
            
            message = (
                f"*New Parking Lot: {lot.name}* \n"
                f"{lot.address} |  ₹{lot.price_per_hour}/hr\n"
                f"*Open for bookings now!*"
            )
            return send_gchat_notification(message)
    except Exception as e:
        if "Lot not visible" in str(e): raise e
        print(f"[ERROR] {e}")