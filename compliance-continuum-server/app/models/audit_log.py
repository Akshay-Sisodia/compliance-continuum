"""
audit_log.py

This module defines enums for audit log actions and compliance status for use in audit logging and compliance tracking.
- ActionType: Enum for the type of action performed (CRUD, ACCESS)
- ComplianceStatus: Enum for compliance result/status

Note: SQLAlchemy ORM code removed; only Pydantic models/enums are used for Supabase integration.
"""

import uuid
from sqlalchemy import Column, String, DateTime, Enum as SqlEnum, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from datetime import datetime
from enum import Enum

class ActionType(str, Enum):
    """
    Enum representing the type of action performed for audit logging.
    - CREATE: Resource creation
    - UPDATE: Resource update
    - DELETE: Resource deletion
    - ACCESS: Resource access/read
    """
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    ACCESS = "ACCESS"

class ComplianceStatus(str, Enum):
    """
    Enum representing the compliance status of an action or resource.
    - COMPLIANT: Meets all compliance requirements
    - NON_COMPLIANT: Fails one or more compliance checks
    - UNKNOWN: Compliance not determined
    """
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    UNKNOWN = "UNKNOWN"

# SQLAlchemy ORM removed. Use only Pydantic models for Supabase integration.
