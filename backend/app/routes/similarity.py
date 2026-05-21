from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.auth import get_current_user
from app.db.deps import get_db
from app.models.project import Project
from app.models.repository import Repository
from app.models.user import User, UserRole
from app.schemas.similarity import (
    SimilarityAnalysisResponse,
    SimilarityRepositoryItem,
)
from app.services.dolos_service import get_dolos_status

router = APIRouter()


@router.get("/similarity/dolos/status")
def get_similarity_dolos_status(
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in (UserRole.PROFESSOR, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="No puedes consultar el estado de Dolos")

    return get_dolos_status()


@router.post(
    "/projects/{project_id}/similarity/analyze",
    response_model=SimilarityAnalysisResponse,
)
def prepare_similarity_analysis(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    if current_user.role not in (UserRole.PROFESSOR, UserRole.ADMIN):
        raise HTTPException(
            status_code=403,
            detail="No puedes analizar similitud en este proyecto",
        )

    if current_user.role == UserRole.PROFESSOR and project.professor_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="No puedes analizar similitud en este proyecto",
        )

    repos_with_users = (
        db.query(Repository, User)
        .join(User, Repository.student_id == User.id)
        .filter(Repository.project_id == project_id)
        .all()
    )

    if len(repos_with_users) < 2:
        raise HTTPException(
            status_code=422,
            detail="Se necesitan al menos 2 entregas para analizar similitud",
        )

    repositories = [
        SimilarityRepositoryItem(
            repository_id=str(repo.id),
            student_id=str(user.id),
            student_name=user.full_name,
            student_email=user.email,
            repo_url=repo.repo_url,
            branch=repo.branch,
        )
        for repo, user in repos_with_users
    ]

    return SimilarityAnalysisResponse(
        project_id=str(project.id),
        status="READY",
        message="Analisis de similitud preparado para integrar Dolos",
        repositories_count=len(repositories),
        repositories=repositories,
    )
