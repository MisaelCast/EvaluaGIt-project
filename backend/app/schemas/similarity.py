from pydantic import BaseModel, Field


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
    pairs: list = Field(default_factory=list)
    provider: str = "dolos"
    executed: bool = False
