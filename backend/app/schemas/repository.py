from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RepositoryCreate(BaseModel):
    project_id: UUID
    repo_url: str
    branch: str = "main"


class RepositoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    student_id: UUID
    repo_url: str
    branch: str
    status: str
    last_commit_hash: str | None
    last_analyzed_at: datetime | None
    created_at: datetime
    updated_at: datetime
