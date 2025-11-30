from celery import Celery
from celery.schedules import crontab
from celery import signals
import os
from dotenv import load_dotenv

load_dotenv()

TASK_MODULES = [
    'tasks.csv_export',
    'tasks.daily_reminders',
    'tasks.monthly_report',
    'tasks.gchat_notifications'
]

# Create Celery instance and instruct it to import task modules
celery_app = Celery(__name__, include=TASK_MODULES)

REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Celery configuration
celery_app.conf.update(
    broker_url=REDIS_URL,
    result_backend=REDIS_URL,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Kolkata',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,   # 30 minutes hard limit
    task_soft_time_limit=25 * 60,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        'daily-reminders': {
            'task': 'tasks.daily_reminders',
            'schedule': crontab(hour=19, minute=0),
            'options': {'queue': 'default'}
        },
        'monthly-report': {
            'task': 'tasks.monthly_report',
            'schedule': crontab(day_of_month=1, hour=10, minute=0),
            'options': {'queue': 'default'}
        },
    }
)

# Global app reference for Celery tasks
_app = None

def set_app(app):
    """Set the Flask app instance for Celery tasks"""
    global _app
    _app = app

def make_celery(app):
    """Initialize Celery with Flask app"""
    set_app(app)
    
    class ContextTask(celery_app.Task):
        """Make celery tasks work with Flask app context"""
        def __call__(self, *args, **kwargs):
            with _app.app_context():
                return self.run(*args, **kwargs)
    
    celery_app.Task = ContextTask
    return celery_app


# Worker initialization.. when Celery worker starts, initialize Flask app
@celery_app.on_after_configure.connect
def setup_app_context(sender=None, **kwargs):
    """
    Try to initialize Flask app for Celery worker.
    First try normal `from app import create_app`. If that fails (e.g. because worker
    was started from a different cwd), insert the backend directory into sys.path and retry.
    """
    import importlib, os, sys
    #  Try normal import first
    try:
        from app import create_app
        app = create_app()
        set_app(app)
        print("Flask app initialized for worker")
        return
    except Exception as e:
        print(f"Could not initialize Flask app on startup: {e}")

    base = os.path.dirname(os.path.abspath(__file__))  
    if base not in sys.path:
        sys.path.insert(0, base)
        print(f"Inserted {base} into sys.path for fallback import")

    try:
        create_app = importlib.import_module("app").create_app
        app = create_app()
        set_app(app)
        print("Flask app initialized for worker (fallback)")
    except Exception as e:
        print(f"Fallback import failed: {e}")


@signals.task_prerun.connect
def task_prerun(sender=None, task_id=None, task=None, **kwargs):
    if not _app:
        try:
            from app import create_app
            app = create_app()
            set_app(app)
            print(f"App context initialized for task {task.name}")
        except Exception as e:
            print(f"Failed to initialize app for task: {e}")