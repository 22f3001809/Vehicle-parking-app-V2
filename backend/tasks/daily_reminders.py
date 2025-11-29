from celery import shared_task
from models import db, User, Reservation, ParkingLot
from datetime import datetime, timedelta
import pytz
from .email import send_email

print("[TASK] Daily reminders module loaded")

def get_app():
    try:
        from celery_app import _app
        if _app: return _app
        from app import create_app
        return create_app()
    except ImportError:
        from app import create_app
        return create_app()

@shared_task(name='tasks.daily_reminders')
def daily_reminders():
    print("[TASK] Starting daily reminders job...")
    app = get_app()
    
    with app.app_context():
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        # 1. CHECK INACTIVE USERS
        seven_days_ago = now - timedelta(days=7)
        seven_days_ago_utc = seven_days_ago.astimezone(pytz.utc).replace(tzinfo=None)
        
        inactive_users = db.session.execute(
            db.text("""
                SELECT id, email, full_name FROM users 
                WHERE is_admin = 0 
                AND id NOT IN (
                    SELECT user_id FROM reservations 
                    WHERE booking_timestamp > :date
                )
            """),
            {'date': seven_days_ago_utc}
        ).fetchall()
        
        for u in inactive_users:
            try:
                send_email("We miss you!", u.email, f"Hi {u.full_name}, come back and park with us!")
                print(f"[SENT] Inactive reminder to {u.email}")
            except: pass

        # 2. CHECK PENDING RESERVATIONS OLDER THAN 2 HOURS
        two_hours_ago = now - timedelta(hours=2)
        two_hours_ago_utc = two_hours_ago.astimezone(pytz.utc).replace(tzinfo=None)
        
        pending_res = Reservation.query.filter(
            Reservation.status == 'pending',
            Reservation.booking_timestamp < two_hours_ago_utc
        ).all()
        
        for res in pending_res:
            try:
                user = User.query.get(res.user_id)
                lot_name = "Unknown Lot"
                if res.parking_spot and res.parking_spot.parking_lot:
                    lot_name = res.parking_spot.parking_lot.name

                send_email(
                    "Action Required: Pending Reservation", 
                    user.email, 
                    f"Hi {user.full_name}, your reservation at {lot_name} is pending check-in."
                )
                print(f"[SENT] Check-in reminder to {user.email}")
            except Exception as e:
                print(f"[ERROR] Reminder failed: {e}")

    return {'status': 'success'}