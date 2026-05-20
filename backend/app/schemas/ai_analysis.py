from typing import Any

from pydantic import BaseModel, Field


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
