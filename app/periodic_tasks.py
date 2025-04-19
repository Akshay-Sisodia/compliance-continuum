from celery.schedules import crontab
from app.celery_worker import celery, update_cve_db_task, run_owasp_scan_task
import os

def setup_periodic_tasks():
    # Update CVE DB every day at midnight
    celery.conf.beat_schedule = {
        'update-cve-db-daily': {
            'task': 'app.celery_worker.update_cve_db_task',
            'schedule': crontab(hour=0, minute=0),
        },
        'run-owasp-scan-daily': {
            'task': 'app.celery_worker.run_owasp_scan_task',
            'schedule': crontab(hour=1, minute=0),
            'args': (os.getenv('OWASP_SCAN_DIR', '.'),)
        }
    }
