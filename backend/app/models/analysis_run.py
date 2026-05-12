import uuid
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, JSON, String, func
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class AnalysisRunStatus(str, PyEnum):
    """Estados posibles de una ejecución de análisis."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AnalysisRun(Base):
    """Modelo que registra cada ejecución de análisis sobre un repositorio."""

    __tablename__ = "analysis_runs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    repository_id = Column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id"),
        nullable=False,
    )
    status = Column(
        Enum(AnalysisRunStatus, name="analysisrunstatus"),
        nullable=False,
        default=AnalysisRunStatus.PENDING,
    )
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    commit_hash = Column(String, nullable=True)
    result_json = Column(JSON, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
