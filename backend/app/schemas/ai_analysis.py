from typing import Any
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AiAnalysisResponse(BaseModel):
    enabled: bool
    provider: str
    summary: str | None = None
    quality_score: int | None = None
    strengths: list[str] = Field(default_factory=list)
    issues: list[dict[str, Any]] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    risk_level: str | None = None
    files_count: int | None = None
    message: str | None = None
    error: str | None = None


class AiAnalysisRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    repository_id: UUID
    status: str
    result_json: dict[str, Any] | None
    error_message: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
