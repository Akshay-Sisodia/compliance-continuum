from celery import Celery, Task
from app.integrations.cve_db import update_cves
from app.integrations.owasp import run_dependency_check
from app.db import SessionLocal
from app.logging_config import setup_logging
import os
import logging

setup_logging()
logger = logging.getLogger("celery_worker")

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery = Celery(
    "compliance_jobs",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

class BaseTaskWithRetry(Task):
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 5, "countdown": 60}
    retry_backoff = True
    retry_jitter = True
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {self.name} failed: {exc}", exc_info=True)
    def on_success(self, retval, task_id, args, kwargs):
        logger.info(f"Task {self.name} succeeded.")

@celery.task(base=BaseTaskWithRetry, bind=True)
def update_cve_db_task(self):
    logger.info("Starting update_cve_db_task")
    try:
        with SessionLocal() as db:
            update_cves(db)
        logger.info("Completed update_cve_db_task")
    except Exception as e:
        logger.error(f"Error in update_cve_db_task: {e}", exc_info=True)
        raise self.retry(exc=e)

@celery.task(base=BaseTaskWithRetry, bind=True)
def run_owasp_scan_task(self, target_dir):
    logger.info(f"Starting run_owasp_scan_task for dir: {target_dir}")
    try:
        run_dependency_check(target_dir)
        logger.info("Completed run_owasp_scan_task")
    except Exception as e:
        logger.error(f"Error in run_owasp_scan_task: {e}", exc_info=True)
        raise self.retry(exc=e)
