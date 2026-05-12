from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AnalysisRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    repository_id: UUID
    status: str
    started_at: datetime | None
    finished_at: datetime | None
    commit_hash: str | None
    result_json: list | dict | None
    error_message: str | None
    created_at: datetime
