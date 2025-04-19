"""
audit.py

This module provides tamper-evident audit logging for compliance events. Each log entry is chained with a SHA-256 hash of its content and the previous log's hash, making the log history tamper-resistant.

Features:
- Add audit log entries with hash chaining
- Query audit logs with filters
- Purge logs older than a retention policy (default: 7 years)
"""

from datetime import datetime, timedelta
from ..db import get_supabase
from ..models.audit_log import ActionType, ComplianceStatus
supabase = get_supabase()

RETENTION_YEARS = 7

import hashlib

def add_audit_log(user_id, action_type, resource_id, changes, compliance_status):
    """
    Add a tamper-evident audit log entry.

    Each entry includes a SHA-256 hash of its content and the previous log's hash, forming a hash chain for integrity.

    Args:
        user_id: ID of the user performing the action.
        action_type: Enum or string describing the action (e.g., CREATE, UPDATE, ACCESS).
        resource_id: ID of the resource affected.
        changes: Dict or JSON-serializable object describing changes or event details.
        compliance_status: Enum or string for compliance result/status.
    
    Returns:
        dict: The inserted audit log record.
    
    Raises:
        Exception: If insertion fails or database error occurs.
    """
    from datetime import datetime
    # Fetch the most recent log to get its hash for chaining
    prev_hash = None
    last_log = supabase.table("audit_logs").select("hash").order("timestamp", desc=True).limit(1).execute()
    if last_log.data and len(last_log.data) > 0:
        prev_hash = last_log.data[0].get("hash")
    data = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": str(user_id),
        "action_type": action_type.value if hasattr(action_type, 'value') else str(action_type),
        "resource_id": str(resource_id),
        "changes": changes,
        "compliance_status": compliance_status.value if hasattr(compliance_status, 'value') else str(compliance_status),
        "prev_hash": prev_hash or "0"  # Genesis hash if first log
    }
    # Compute hash of this entry (excluding the hash field itself)
    hash_input = str(data).encode("utf-8")
    data["hash"] = hashlib.sha256(hash_input).hexdigest()
    res = supabase.table("audit_logs").insert(data).execute()
    if getattr(res, "error", None):
        raise Exception(res.error.message)
    return res.data[0]


# Get audit logs (with optional filters)
def get_audit_logs(user_id=None, resource_id=None, limit=100):
    """
    Query audit logs, optionally filtering by user or resource.

    Args:
        user_id (optional): Only return logs for this user.
        resource_id (optional): Only return logs for this resource.
        limit (int): Max number of logs to return (default: 100).
    
    Returns:
        list: List of audit log records (dicts).
    
    Raises:
        Exception: If query fails or database error occurs.
    """
    query = supabase.table("audit_logs").select("*")
    if user_id:
        query = query.eq("user_id", str(user_id))
    if resource_id:
        query = query.eq("resource_id", str(resource_id))
    query = query.order("timestamp", desc=True).limit(limit)
    res = query.execute()
    if getattr(res, "error", None):
        raise Exception(res.error.message)
    return res.data

# Purge logs older than retention policy using Supabase
def purge_old_logs():
    """
    Permanently delete audit logs older than the retention policy (RETENTION_YEARS).
    
    Returns:
        list: List of deleted log records (if supported by DB).
    
    Raises:
        Exception: If deletion fails or database error occurs.
    """
    cutoff = datetime.utcnow() - timedelta(days=RETENTION_YEARS * 365)
    cutoff_iso = cutoff.isoformat()
    res = supabase.table("audit_logs").delete().lt("timestamp", cutoff_iso).execute()
    # Optionally, check for errors
    if hasattr(res, "error") and res.error:
        raise Exception(res.error.message)
    return res.data
