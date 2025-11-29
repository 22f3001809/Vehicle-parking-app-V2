# tasks/monthly_reports.py
from celery import shared_task
from models import db, User, Reservation, ParkingLot
from datetime import datetime
import pytz
from .email import send_email

def get_app():
    try:
        from celery_app import _app
        if _app: return _app
        from app import create_app
        return create_app()
    except ImportError:
        from app import create_app
        return create_app()

@shared_task(name='tasks.monthly_report')
def monthly_report():
    """Generate and send monthly activity reports to all users"""
    print("[TASK] Starting monthly activity report generation...")
    app = get_app()
    
    with app.app_context():
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_start_utc = month_start.astimezone(pytz.utc).replace(tzinfo=None)
        
        users = User.query.filter_by(is_admin=False).all()
        print(f"[REPORT] Generating reports for {len(users)} users...")
        
        for user in users:
            try:
                reservations = Reservation.query.filter(
                    Reservation.user_id == user.id,
                    Reservation.check_out_timestamp >= month_start_utc
                ).all()
                
                if not reservations:
                    continue
                
                total_bookings = len(reservations)
                total_spent = sum(r.parking_cost or 0 for r in reservations)
                
                lot_usage = {}
                for res in reservations:
                    # Safely access lot via spot
                    if res.parking_spot and res.parking_spot.lot_id:
                        lot_id = res.parking_spot.lot_id
                        lot_usage[lot_id] = lot_usage.get(lot_id, 0) + 1
                
                most_used_lot_name = 'N/A'
                if lot_usage:
                    most_used_lot_id = max(lot_usage, key=lot_usage.get)
                    lot_obj = ParkingLot.query.get(most_used_lot_id)
                    if lot_obj:
                        most_used_lot_name = lot_obj.name 
                
                # Calculate Duration
                total_duration = 0
                completed_count = 0
                for res in reservations:
                    if res.check_in_timestamp and res.check_out_timestamp:
                        duration = (res.check_out_timestamp - res.check_in_timestamp).total_seconds() / 3600
                        total_duration += duration
                        completed_count += 1
                
                avg_duration = total_duration / completed_count if completed_count > 0 else 0
                month_name = month_start.strftime("%B %Y")
                
                html_report = f"""
                <h2>Monthly Parking Report: {month_name}</h2>
                <p><strong>Total Bookings:</strong> {total_bookings}</p>
                <p><strong>Total Spent:</strong> ₹{total_spent:.2f}</p>
                <p><strong>Most Used Lot:</strong> {most_used_lot_name}</p>
                <p><strong>Avg Duration:</strong> {avg_duration:.1f} hours</p>
                <hr>
                <p>Happy Parking!</p>
                """
                
                subject = f" Your Parking Activity Report - {month_name}"
                body = f"Hi {user.full_name}, check your attached report."
                
                send_email(subject, user.email, body, html=html_report)
                print(f"[SENT] Monthly report to {user.email}")
            except Exception as e:
                print(f"[ERROR] Report failed for {user.email}: {e}")
    
    return {'status': 'success'}