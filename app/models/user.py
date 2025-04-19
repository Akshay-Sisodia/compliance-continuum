"""
user.py

This module defines the User model for storing user accounts and authentication data.
- User: Pydantic model for user metadata and credentials

Note: SQLAlchemy ORM code removed; only Pydantic models are used for Supabase integration.
"""

from pydantic import BaseModel
import uuid
from datetime import datetime

class User(BaseModel):
    """
    Pydantic model representing a user account.
    
    Attributes:
        id (uuid.UUID): Unique identifier for the user.
        username (str): Username or login name.
        email (str): User's email address.
        hashed_password (str): Hashed password for authentication.
        is_active (bool): Whether the user account is active.
        is_admin (bool): Whether the user has administrative privileges.
        created_at (datetime): Timestamp when the user was created.
    """
    id: uuid.UUID
    username: str
    email: str
    hashed_password: str
    is_active: bool
    is_admin: bool
    created_at: datetime

# SQLAlchemy ORM removed. Use only Pydantic models for Supabase integration.
