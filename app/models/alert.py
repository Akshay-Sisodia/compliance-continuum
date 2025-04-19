"""
alert.py

This module defines the Alert model and related enums for use in compliance notifications and alerting systems.
- AlertType: Enum for alert criticality
- DeliveryChannel: Enum for notification channels
- Alert: Core alert data structure
- AlertModel: Pydantic model for alert creation/input
"""

from enum import Enum
from pydantic import BaseModel
import uuid
from datetime import datetime

class AlertType(str, Enum):
    """
    Enum representing the criticality of an alert.
    - CRITICAL: Requires immediate attention.
    - IMPORTANT: Important but not critical.
    - INFORMATIONAL: Informational only.
    """
    CRITICAL = "CRITICAL"
    IMPORTANT = "IMPORTANT"
    INFORMATIONAL = "INFORMATIONAL"

class DeliveryChannel(str, Enum):
    """
    Enum representing supported alert delivery channels.
    - EMAIL: Email notification
    - IN_APP: In-app notification
    - WEBHOOK: Webhook call
    - SLACK: Slack channel/message
    """
    EMAIL = "EMAIL"
    IN_APP = "IN_APP"
    WEBHOOK = "WEBHOOK"
    SLACK = "SLACK"

class Alert(BaseModel):
    """
    Data model representing an alert/notification record.
    
    Attributes:
        id (uuid.UUID): Unique identifier for the alert.
        type (str): The alert type (e.g., CRITICAL, IMPORTANT, INFORMATIONAL).
        message (str): The alert message or description.
        severity (str): Severity level (redundant with type, but may be used for external compatibility).
        created_at (datetime): Timestamp when the alert was created.
        read (bool): Whether the alert has been read/dismissed by the user.
    """
    id: uuid.UUID
    type: str
    message: str
    severity: str
    created_at: datetime
    read: bool

class AlertModel(BaseModel):
    """
    Pydantic model for creating or inputting a new alert.
    
    Attributes:
        type (AlertType): The alert type/criticality.
        message (str): The alert message.
        delivery_channels (list[DeliveryChannel]): List of delivery channels to notify.
        created_at (str): Timestamp (ISO format) when the alert was created.
    """
    type: AlertType
    message: str
    delivery_channels: list[DeliveryChannel]
    created_at: str
