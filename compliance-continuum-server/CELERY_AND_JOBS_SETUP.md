# Compliance Continuum: Celery & Scheduled Jobs Setup

This guide documents the steps required to enable and run scheduled compliance jobs (CVE/NVD updates, OWASP scans) using Celery and Redis.

---

## 1. Install Required Dependencies

- Make sure the following are in your `requirements.txt`:
  - celery
  - redis

Install if missing:
```sh
uv pip install celery redis
```

---

## 2. Redis Server

- Start a Redis server locally (or use a managed Redis instance).
  - Default URL: `redis://localhost:6379/0`

---

## 3. Celery Worker & Beat Setup

- **Celery worker:** Handles background jobs.
- **Celery beat:** Schedules periodic jobs.

### Start the worker:
```sh
celery -A app.celery_worker.celery worker --loglevel=info
```

### Start the beat scheduler:
```sh
celery -A app.celery_worker.celery beat --loglevel=info
```

---

## 4. Periodic Jobs Configured

- **CVE/NVD DB Update:**
  - Task: `app.celery_worker.update_cve_db_task`
  - Runs daily at midnight (00:00)
- **OWASP Dependency-Check Scan:**
  - Task: `app.celery_worker.run_owasp_scan_task`
  - Runs daily at 1am (01:00)
  - Directory scanned: set via `OWASP_SCAN_DIR` env var (default is project root)

---

## 5. Environment Variables

- `CELERY_BROKER_URL` (default: `redis://localhost:6379/0`)
- `CELERY_RESULT_BACKEND` (default: `redis://localhost:6379/0`)
- `OWASP_SCAN_DIR` (default: `.`)

---

## 6. Troubleshooting

- Ensure Redis is running and accessible.
- Check Celery logs for errors.
- Make sure the Dependency-Check CLI is installed and available in your PATH for OWASP scans.

---

## 7. Manual Trigger

You can manually trigger the jobs from a Python shell:
```python
from app.celery_worker import update_cve_db_task, run_owasp_scan_task
update_cve_db_task.delay()
run_owasp_scan_task.delay("<target_dir>")
```

---

## 8. Extending

- To add more scheduled jobs, edit `app/periodic_tasks.py` and register new tasks with `celery.conf.beat_schedule`.
- For custom intervals, adjust the `crontab` schedule accordingly.

---

## 9. References
- [Celery Docs](https://docs.celeryq.dev/en/stable/)
- [OWASP Dependency-Check](https://jeremylong.github.io/DependencyCheck/)
- [NVD Data Feeds](https://nvd.nist.gov/vuln/data-feeds)

---
