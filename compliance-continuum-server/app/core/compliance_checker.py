import re
from typing import List, Dict
from sqlalchemy.orm import Session
from ..models.regulatory_rule import RegulatoryRule

"""
compliance_checker.py

This module provides a comprehensive set of static and dynamic compliance checks for source code. It detects:
- PII (Personally Identifiable Information) patterns (e.g., SSN, credit card, email, phone, address, passport, PAN, GSTIN)
- Vulnerabilities (dangerous functions, insecure imports, weak cryptography, hardcoded secrets)
- GDPR violations (export, delete, transfer of user data without consent, biometric storage)
- Discriminatory logic (checks on protected attributes)
- Dynamic regulatory rules (fetched from the database)
- External API-based vulnerability scanning
- ML-based code risk analysis

All patterns are language-agnostic and designed to catch common edge cases.
"""

# PII patterns: SSN, credit card, email, phone, address, passport, etc.
PII_PATTERNS = [
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # US SSN
    re.compile(r"\b\d{16}\b"),  # Credit card (basic)
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),  # Email
    re.compile(r"\b\d{10}\b"),  # Phone (generic)
    re.compile(r"passport\s*number\s*[:=]\s*['\"]?\w+['\"]?", re.IGNORECASE),
    re.compile(r"address\s*[:=]\s*['\"]?.+['\"]?", re.IGNORECASE),
    re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b"),  # PAN (India)
    re.compile(r"\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}\d{1}[Z]{1}[A-Z0-9]{1}\b"),  # GSTIN (India)
]

# Vulnerabilities: dangerous functions, insecure imports, weak crypto, etc.
VULNERABILITY_PATTERNS = [
    re.compile(r"eval\s*\("),
    re.compile(r"exec\s*\("),
    re.compile(r"subprocess\.Popen"),
    re.compile(r"os\.system"),
    re.compile(r"pickle\.load"),
    re.compile(r"yaml\.load\("),
    re.compile(r"input\s*\("),
    re.compile(r"md5\("),
    re.compile(r"sha1\("),
    re.compile(r"random\.random\("),
    re.compile(r"import\s+base64"),
    # Added patterns for hardcoded credentials and secrets
    re.compile(r"password\s*=\s*['\"].+['\"]", re.IGNORECASE),
    re.compile(r"passwd\s*=\s*['\"].+['\"]", re.IGNORECASE),
    re.compile(r"secret\s*=\s*['\"].+['\"]", re.IGNORECASE),
    re.compile(r"api[_-]?key\s*=\s*['\"].+['\"]", re.IGNORECASE),
    re.compile(r"token\s*=\s*['\"].+['\"]", re.IGNORECASE),
    re.compile(r"access[_-]?key\s*=\s*['\"].+['\"]", re.IGNORECASE),
]

# GDPR: export/delete/transfer of personal/user data, lack of consent, etc.
GDPR_PATTERNS = [
    re.compile(r"export.*personal.*data", re.IGNORECASE),
    re.compile(r"delete.*user.*data", re.IGNORECASE),
    re.compile(r"transfer.*user.*data", re.IGNORECASE),
    re.compile(r"without.*consent", re.IGNORECASE),
    re.compile(r"store.*biometric", re.IGNORECASE),
]

# Discrimination: explicit or implicit checks on protected attributes
DISCRIMINATION_PATTERNS = [
    re.compile(r"if.*(gender|race|ethnicity|religion|age|disability|pregnan(y|t)).*==", re.IGNORECASE),
    re.compile(r"for.*(gender|race|ethnicity|religion|age|disability|pregnan(y|t)).*in", re.IGNORECASE),
    re.compile(r"(male|female|black|white|asian|hispanic|muslim|christian|jewish|hindu|atheist)", re.IGNORECASE),
]

def check_pii(code: str) -> List[str]:
    """
    Scan the code for patterns matching PII (Personally Identifiable Information).
    
    Args:
        code (str): The code to scan.
    
    Returns:
        List[str]: List of regex patterns that matched PII in the code.
    """
    return [pat.pattern for pat in PII_PATTERNS if pat.search(code)]

def check_vulnerabilities(code: str) -> List[str]:
    """
    Scan the code for patterns matching common security vulnerabilities (dangerous functions, insecure imports, weak cryptography, hardcoded secrets).
    
    Args:
        code (str): The code to scan.
    
    Returns:
        List[str]: List of regex patterns that matched vulnerabilities in the code.
    """
    return [pat.pattern for pat in VULNERABILITY_PATTERNS if pat.search(code)]

def check_gdpr(code: str) -> List[str]:
    """
    Scan the code for patterns indicating possible GDPR violations (such as export, deletion, or transfer of user data without consent).
    
    Args:
        code (str): The code to scan.
    
    Returns:
        List[str]: List of regex patterns that matched GDPR-violating logic.
    """
    return [pat.pattern for pat in GDPR_PATTERNS if pat.search(code)]

def detect_discriminatory_patterns(code: str) -> List[str]:
    """
    Scan the code for patterns matching discriminatory logic (explicit or implicit checks on protected attributes).
    
    Args:
        code (str): The code to scan.
    
    Returns:
        List[str]: List of regex patterns that matched discriminatory logic.
    """
    return [pat.pattern for pat in DISCRIMINATION_PATTERNS if pat.search(code)]

from app.db import get_supabase
import os
from app.core.external_api import check_external_vulnerabilities
from app.core.ml_analysis import ml_code_analysis
from app.core.policy_engine import evaluate_policy

def run_compliance_checks(code: str, db: object = None, user_id: str = None, resource_id: str = None) -> Dict[str, list]:
    """
    Run all compliance checks on the provided code and return a dictionary of violations found.

    Checks include:
        - PII detection
        - Security vulnerabilities
        - GDPR violations
        - Discriminatory logic
        - Dynamic regulatory rules (from DB)
        - External API-based vulnerability scanning
        - ML-based code analysis

    Args:
        code (str): The code to check.
        db (object, optional): Database connection or session (not always required).
        user_id (str, optional): User ID for audit logging and policy evaluation.
        resource_id (str, optional): Resource ID for audit logging and policy evaluation.
    
    Returns:
        Dict[str, list]: Dictionary mapping check categories to lists of violations or matched patterns.
    """
    violations = {
        # Boolean flags from ethical_enforcer wrappers, which use the check_* functions
        "pii": detect_pii(code),
        "vulnerabilities": detect_security_vulnerabilities(code),
        "gdpr": detect_gdpr_violations(code),
        "discrimination": detect_discriminatory_patterns(code),
        "regulatory_rules_violations": [],
    }

    # Advanced modules config (set via env or config file)
    # These flags allow dynamic enabling/disabling of advanced compliance modules
    ENABLE_EXTERNAL_API = os.getenv("ENABLE_EXTERNAL_API", "true").lower() == "true"
    ENABLE_ML_ANALYSIS = os.getenv("ENABLE_ML_ANALYSIS", "true").lower() == "true"
    ENABLE_POLICY_ENGINE = os.getenv("ENABLE_POLICY_ENGINE", "true").lower() == "true"

    # External compliance API integration
    if ENABLE_EXTERNAL_API:
        # Use an external service for vulnerability scanning (stubbed in external_api.py)
        violations["external_api_vulnerabilities"] = check_external_vulnerabilities(code)

    # ML-based code analysis
    if ENABLE_ML_ANALYSIS:
        # Use ML model for risk scoring (stubbed in ml_analysis.py)
        violations["ml_analysis"] = ml_code_analysis(code)

    # Granular policy engine (dynamic regulatory rules)
    if ENABLE_POLICY_ENGINE:
        # Evaluate dynamic regulatory rules from DB; pass user/resource info for audit
        violations["regulatory_rules_violations"] = evaluate_policy(code, user_id=user_id, resource_id=resource_id)

    return violations
    supabase = get_supabase()
    reg_rules_resp = supabase.table("regulatory_rules").select("id, name, description, pattern, enabled").eq("enabled", True).execute()
    violations = []
    if getattr(reg_rules_resp, "data", None):
        for rule in reg_rules_resp.data:
            try:
                pattern = rule["pattern"]
                regex = re.compile(pattern)
                if regex.search(code):
                    violations.append({
                        "rule_id": rule["id"],
                        "name": rule["name"],
                        "description": rule["description"],
                        "pattern": pattern
                    })
            except Exception as e:
                continue  # Ignore invalid regex
    results["regulatory_rules_violations"] = violations
    return results
