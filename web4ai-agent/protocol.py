"""Script.god protocol transport/message layer. Reusable across any participant —
does not contain Lola-specific logic. See agent.py for that."""

from enum import Enum
from typing import Any, Optional
from datetime import datetime, timezone
from uuid import uuid4
from pydantic import BaseModel, Field


class MessageType(str, Enum):
    CONNECT = "CONNECT"
    CAPABILITIES = "CAPABILITIES"
    TASK = "TASK"
    ACK = "ACK"
    CONTEXT = "CONTEXT"
    PROGRESS = "PROGRESS"
    RESULT = "RESULT"
    VERIFY = "VERIFY"
    SYNC = "SYNC"
    ERROR = "ERROR"
    BLOCKED = "BLOCKED"
    CANCEL = "CANCEL"


class Envelope(BaseModel):
    type: MessageType
    id: str = Field(default_factory=lambda: str(uuid4()))
    correlation_id: Optional[str] = None
    from_: str = Field(alias="from")
    to: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, Any]

    class Config:
        populate_by_name = True


class FailureTracker:
    """Enforces halt-after-two-consecutive-failures (non-negotiable per the
    LMLM architecture doc — no unbounded retry loops)."""

    def __init__(self) -> None:
        self.count = 0

    def record_failure(self) -> bool:
        """Returns True once BLOCKED should be emitted instead of retrying."""
        self.count += 1
        return self.count >= 2

    def reset(self) -> None:
        self.count = 0
