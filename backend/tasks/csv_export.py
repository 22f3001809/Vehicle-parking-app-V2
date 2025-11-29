from celery import shared_task
from models import db, User, Reservation, ParkingLot
from datetime import datetime
import csv
import io
from .email import send_email
import os

def get_app():
    """Get the Flask app instance for Celery tasks"""
    try:
        from celery_app import _app
        if _app: return _app
        from app import create_app
        return create_app()
    except ImportError:
        from app import create_app
        return create_app()

@shared_task(name='tasks.csv_export')
def export_csv_task(user_id):
    """Generate CSV export of user's parking history and send via email"""
    print(f"[TASK] Starting CSV export for user {user_id}...")
    
    try:
        app = get_app()
        
        with app.app_context():
            user = User.query.get(user_id)
            if not user:
                print(f"[ERROR] User {user_id} not found")
                return {'status': 'error', 'message': 'User not found'}
            
            # Get reservations
            reservations = Reservation.query.filter_by(user_id=user_id).all()
            print(f"[EXPORT] Generating CSV for {len(reservations)} reservations...")
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'Reservation ID', 'Parking Lot', 'Spot Number', 'Vehicle Number',
                'Booking Date', 'Check-in Time', 'Check-out Time', 'Duration (Hours)',
                'Price per Hour', 'Total Cost', 'Status'
            ])
            
            for res in reservations:
                # Initialize default values
                lot_name = 'N/A'
                spot_num = 'N/A'
                price = 'N/A'
                
    
                if res.parking_spot:
                    spot_num = res.parking_spot.spot_number
                    
                    #  Check if lot exists attached to spot
                    if res.parking_spot.parking_lot:
                        lot = res.parking_spot.parking_lot
                        lot_name = lot.name  
                        price = lot.price_per_hour

                duration = 'N/A'
                if res.check_in_timestamp and res.check_out_timestamp:
                    duration_hours = (res.check_out_timestamp - res.check_in_timestamp).total_seconds() / 3600
                    duration = f"{duration_hours:.2f}"
                
                writer.writerow([
                    res.id,
                    lot_name,
                    spot_num,
                    res.vehicle_number,
                    res.booking_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    res.check_in_timestamp.strftime('%Y-%m-%d %H:%M:%S') if res.check_in_timestamp else 'N/A',
                    res.check_out_timestamp.strftime('%Y-%m-%d %H:%M:%S') if res.check_out_timestamp else 'N/A',
                    duration,
                    price,
                    res.parking_cost if res.parking_cost else 'N/A',
                    res.status
                ])
            
            csv_content = output.getvalue()
            output.close()
            
            # Send email
            filename = f"parking_history_{user.username}_{datetime.now().strftime('%Y%m%d')}.csv"
            subject = "Your Parking History Export"
            body = f"""Hello {user.full_name},

Your parking history export is ready. Please find the attached CSV file.

Happy parking!
Parking App Team"""
            
            attachments = [(filename, csv_content, 'text/csv')]
            send_email(subject, user.email, body, attachments=attachments)
            
            print(f"[SENT] CSV export to {user.email}")
            return {'status': 'success', 'filename': filename}
    
    except Exception as e:
        print(f"[ERROR] CSV export failed: {e}")
        import traceback
        traceback.print_exc()
        return {'status': 'error', 'message': str(e)}