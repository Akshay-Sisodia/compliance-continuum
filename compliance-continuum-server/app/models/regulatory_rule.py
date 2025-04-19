"""
regulatory_rule.py

This module defines the RegulatoryRule model for storing and managing regulatory rules (typically regex patterns) for compliance checking.
- RegulatoryRule: Pydantic model for regulatory rule metadata and pattern

Note: SQLAlchemy ORM code removed; only Pydantic models are used for Supabase integration.
"""

from pydantic import BaseModel
import uuid
from datetime import datetime

class RegulatoryRule(BaseModel):
    """
    Pydantic model representing a regulatory rule for compliance checking.
    
    Attributes:
        id (uuid.UUID): Unique identifier for the rule.
        name (str): Name/title of the rule.
        description (str): Description of what the rule checks for.
        pattern (str): Regex pattern for detecting violations.
        enabled (bool): Whether the rule is currently active.
        created_at (datetime): Timestamp when the rule was created.
        updated_at (datetime): Timestamp when the rule was last updated.
    """
    id: uuid.UUID
    name: str
    description: str
    pattern: str
    enabled: bool
    created_at: datetime
    updated_at: datetime

# SQLAlchemy ORM removed. Use only Pydantic models for Supabase integration.
