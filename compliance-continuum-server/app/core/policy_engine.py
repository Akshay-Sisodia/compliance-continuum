"""
policy_engine.py

This module provides a dynamic policy engine for evaluating code against regulatory rules stored in the database.

Features:
- Load enabled regulatory rules (regex patterns, descriptions, etc.)
- Evaluate code against all rules and collect violations
- Optionally log evaluation results to the audit log for traceability
"""

import re
from typing import Any, Dict, List
from app.db import get_supabase
from app.models.regulatory_rule import RegulatoryRule
from app.core.audit import add_audit_log, ComplianceStatus, ActionType

supabase = get_supabase()

def load_policies(enabled_only: bool = True) -> List[Dict[str, Any]]:
    """
    Load regulatory rules (policies) from the database.

    Args:
        enabled_only (bool): If True, only return enabled rules.
    
    Returns:
        List[Dict[str, Any]]: List of policy records (each as a dict).
    
    Raises:
        Exception: If database query fails.
    """
    query = supabase.table("regulatory_rules").select("*")
    if enabled_only:
        query = query.eq("enabled", True)
    res = query.execute()
    if getattr(res, "error", None):
        raise Exception(res.error.message)
    return res.data

def evaluate_policy(code: str, user_id: str = None, resource_id: str = None) -> List[Dict[str, Any]]:
    """
    Evaluate the provided code against all enabled regulatory rules (policies).

    Args:
        code (str): The code to evaluate.
        user_id (str, optional): User ID for audit logging.
        resource_id (str, optional): Resource ID for audit logging.
    
    Returns:
        List[Dict[str, Any]]: List of violations, each containing rule metadata and matches.
    
    Side Effects:
        Optionally logs the evaluation and its result to the audit log (if user_id and resource_id are provided).
    """
    policies = load_policies(enabled_only=True)
    violations = []
    for rule in policies:
        pattern = rule["pattern"]
        try:
            regex = re.compile(pattern, re.MULTILINE)
            matches = regex.findall(code)
            if matches:
                violations.append({
                    "rule_id": rule["id"],
                    "name": rule["name"],
                    "description": rule["description"],
                    "pattern": pattern,
                    "matches": matches
                })
        except re.error as e:
            # Invalid regex in rule
            continue
    # Audit log (optional)
    if user_id and resource_id:
        status = ComplianceStatus.NON_COMPLIANT if violations else ComplianceStatus.COMPLIANT
        add_audit_log(
            user_id=user_id,
            action_type=ActionType.ACCESS,
            resource_id=resource_id,
            changes={"violations": violations},
            compliance_status=status
        )
    return violations
