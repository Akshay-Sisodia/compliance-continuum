"""
cve.py

This module defines the CVE (Common Vulnerabilities and Exposures) model for storing and transferring vulnerability data.
- CVE: Pydantic model for CVE details

Note: SQLAlchemy ORM code removed; only Pydantic models are used for Supabase integration.
"""

from pydantic import BaseModel
import uuid
from datetime import datetime
from typing import Any

class CVE(BaseModel):
    """
    Pydantic model representing a Common Vulnerability and Exposure (CVE) record.
    
    Attributes:
        id (str): CVE identifier (e.g., CVE-2023-12345).
        description (str): Description of the vulnerability.
        published (datetime): Date/time when the CVE was published.
        last_modified (datetime): Date/time of last modification.
        references (Any): References/links to more information (format may vary).
        cvss (Any): CVSS (Common Vulnerability Scoring System) data (format may vary).
        raw (Any): Raw CVE data as received from source.
    """
    id: str
    description: str
    published: datetime
    last_modified: datetime
    references: Any
    cvss: Any
    raw: Any

# SQLAlchemy ORM removed. Use only Pydantic models for Supabase integration.
