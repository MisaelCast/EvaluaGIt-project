from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.auth import get_current_user
from app.db.deps import get_db
from app.models.project import Project
from app.models.repository import Repository
from app.models.user import User, UserRole
from app.schemas.ai_analysis import AiAnalysisResponse
from app.services.ai_feedback_service import generate_ai_feedback
from app.services.clone_service import CloneError, cleanup_repo, clone_repository
from app.services.repo_validator import validate_branch, validate_repo_url

router = APIRouter()


def _can_run_ai_analysis(repo: Repository, current_user: User, db: Session) -> bool:
    if current_user.role == UserRole.ADMIN:
        return True

    if current_user.role == UserRole.STUDENT:
        return repo.student_id == current_user.id

    if current_user.role == UserRole.PROFESSOR:
        project = db.query(Project).filter(
            Project.id == repo.project_id,
            Project.professor_id == current_user.id,
        ).first()
        return project is not None

    return False


@router.post("/{repo_id}/ai-analysis", response_model=AiAnalysisResponse)
def analyze_repository_with_ai(
    repo_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repositorio no encontrado")

    if not _can_run_ai_analysis(repo, current_user, db):
        raise HTTPException(status_code=403, detail="No puedes analizar este repositorio con IA")

    try:
        validated_url = validate_repo_url(repo.repo_url)
        validated_branch = validate_branch(repo.branch)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    repo_path: str | None = None
    try:
        repo_path = clone_repository(validated_url, validated_branch)
        return generate_ai_feedback(repo_path)

    except CloneError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo completar el analisis IA") from exc

    finally:
        if repo_path:
            cleanup_repo(repo_path)
