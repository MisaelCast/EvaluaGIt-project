from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.auth import get_current_user
from app.db.deps import get_db
from app.models.ai_analysis_run import AiAnalysisRun
from app.models.project import Project
from app.models.repository import Repository
from app.models.user import User, UserRole
from app.schemas.ai_analysis import AiAnalysisRunResponse
from app.services.ai_feedback_service import generate_ai_feedback
from app.services.clone_service import CloneError, cleanup_repo, clone_repository
from app.services.repo_validator import validate_branch, validate_repo_url

router = APIRouter()

AI_STATUS_PENDING = "PENDING"
AI_STATUS_RUNNING = "RUNNING"
AI_STATUS_COMPLETED = "COMPLETED"
AI_STATUS_FAILED = "FAILED"


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


@router.post("/{repo_id}/ai-analysis", response_model=AiAnalysisRunResponse)
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

    ai_run = AiAnalysisRun(
        repository_id=repo.id,
        status=AI_STATUS_PENDING,
    )
    db.add(ai_run)
    db.commit()
    db.refresh(ai_run)

    repo_path: str | None = None
    try:
        ai_run.status = AI_STATUS_RUNNING
        ai_run.started_at = datetime.utcnow()
        db.commit()

        validated_url = validate_repo_url(repo.repo_url)
        validated_branch = validate_branch(repo.branch)
        repo_path = clone_repository(validated_url, validated_branch)
        ai_run.result_json = generate_ai_feedback(repo_path)
        ai_run.status = AI_STATUS_COMPLETED
        ai_run.finished_at = datetime.utcnow()
        db.commit()
        db.refresh(ai_run)
        return ai_run

    except (CloneError, ValueError) as exc:
        db.rollback()
        ai_run.status = AI_STATUS_FAILED
        ai_run.error_message = str(exc)
        ai_run.finished_at = datetime.utcnow()
        db.commit()
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    except Exception as exc:
        db.rollback()
        ai_run.status = AI_STATUS_FAILED
        ai_run.error_message = str(exc)
        ai_run.finished_at = datetime.utcnow()
        db.commit()
        raise HTTPException(status_code=500, detail="No se pudo completar el analisis IA") from exc

    finally:
        if repo_path:
            cleanup_repo(repo_path)


@router.get("/{repo_id}/ai-analysis/latest", response_model=AiAnalysisRunResponse)
def get_latest_ai_analysis(
    repo_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repositorio no encontrado")

    if not _can_run_ai_analysis(repo, current_user, db):
        raise HTTPException(status_code=403, detail="No puedes analizar este repositorio con IA")

    ai_run = (
        db.query(AiAnalysisRun)
        .filter(AiAnalysisRun.repository_id == repo.id)
        .order_by(AiAnalysisRun.created_at.desc())
        .first()
    )
    if not ai_run:
        raise HTTPException(status_code=404, detail="No hay analisis IA para este repositorio")

    return ai_run
