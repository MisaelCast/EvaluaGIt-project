from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SimilarityRepositoryItem(BaseModel):
    repository_id: str
    student_id: str
    student_name: str | None
    student_email: str | None
    repo_url: str
    branch: str


class SimilarityAnalysisResponse(BaseModel):
    project_id: str
    status: str
    message: str
    repositories_count: int
    repositories: list[SimilarityRepositoryItem]
    pairs: list[dict] = Field(default_factory=list)
    provider: str = "dolos"
    executed: bool = False
    raw_output: str | None = None
    output_files: list[str] = Field(default_factory=list)
    summary: dict | None = None


class SimilarityRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    status: str
    result_json: SimilarityAnalysisResponse | None
    error_message: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
