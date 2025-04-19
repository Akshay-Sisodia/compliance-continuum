"""
policy.py

This module defines the Policy model for storing compliance or security policies.
- Policy: Pydantic model for policy metadata and content

Note: SQLAlchemy ORM code removed; only Pydantic models are used for Supabase integration.
"""

from pydantic import BaseModel
import uuid
from datetime import datetime

class Policy(BaseModel):
    """
    Pydantic model representing a compliance or security policy.
    
    Attributes:
        id (uuid.UUID): Unique identifier for the policy.
        name (str): Name/title of the policy.
        description (str): Short description of the policy.
        content (str): Full policy text or rules.
        enabled (bool): Whether the policy is active/enabled.
        created_at (datetime): Timestamp when the policy was created.
        updated_at (datetime): Timestamp when the policy was last updated.
    """
    id: uuid.UUID
    name: str
    description: str
    content: str
    enabled: bool
    created_at: datetime
    updated_at: datetime

# SQLAlchemy ORM removed. Use only Pydantic models for Supabase integration.
