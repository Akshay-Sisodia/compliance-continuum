import threading
import time
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.integrations.cve_db import update_cves
from app.integrations.owasp import run_dependency_check

def cve_update_job(interval_hours=24):
    def job():
        while True:
            with SessionLocal() as db:
                update_cves(db)
            time.sleep(interval_hours * 3600)
    t = threading.Thread(target=job, daemon=True)
    t.start()

def owasp_update_job(target_dir, interval_hours=24):
    def job():
        while True:
            run_dependency_check(target_dir)
            time.sleep(interval_hours * 3600)
    t = threading.Thread(target=job, daemon=True)
    t.start()
