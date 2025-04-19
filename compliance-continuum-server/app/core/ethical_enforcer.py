"""
ethical_enforcer.py

This module provides Boolean wrappers for compliance checks, making it easy to flag code as compliant or non-compliant for:
- PII
- Security vulnerabilities
- Discriminatory logic
- GDPR violations
- Simple ML-based pattern detection

These wrappers are useful for pipelines, API endpoints, or UI integrations where a True/False result is needed.
"""

from .compliance_checker import check_pii, check_vulnerabilities, check_gdpr, detect_discriminatory_patterns

def detect_pii(code: str) -> bool:
    """
    Return True if any PII (Personally Identifiable Information) patterns are detected in the code.
    Args:
        code (str): The code to scan.
    Returns:
        bool: True if PII is detected, False otherwise.
    """
    return bool(check_pii(code))

def detect_security_vulnerabilities(code: str) -> bool:
    """
    Return True if any security vulnerabilities are detected in the code.
    Args:
        code (str): The code to scan.
    Returns:
        bool: True if vulnerabilities are detected, False otherwise.
    """
    return bool(check_vulnerabilities(code))

def detect_discriminatory_patterns(code: str) -> bool:
    """
    Return True if any discriminatory logic is detected in the code.
    Args:
        code (str): The code to scan.
    Returns:
        bool: True if discriminatory logic is detected, False otherwise.
    """
    return bool(detect_discriminatory_patterns(code))

def detect_gdpr_violations(code: str) -> bool:
    """
    Return True if any GDPR violations are detected in the code.
    Args:
        code (str): The code to scan.
    Returns:
        bool: True if GDPR-violating logic is detected, False otherwise.
    """
    return bool(check_gdpr(code))

def ml_pattern_detection(code: str) -> bool:
    """
    Simple ML stub: flag as anomalous if code is very long (simulates ML-based anomaly detection).
    Args:
        code (str): The code to scan.
    Returns:
        bool: True if code length exceeds 2000 characters (simulated anomaly), False otherwise.
    """
    # Simple ML stub: flag if code is very long (simulate anomaly)
    return len(code) > 2000
