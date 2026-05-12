from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
import git
from sqlalchemy.orm import Session

from app.db.auth import get_current_user
from app.db.deps import get_db
from app.models.analysis_run import AnalysisRun, AnalysisRunStatus
from app.models.project import Project
from app.models.repository import Repository, RepositoryStatus
from app.models.user import User, UserRole
from app.schemas.analysis_run import AnalysisRunResponse
from app.services.clone_service import CloneError, cleanup_repo, clone_repository
from app.services.repo_validator import validate_branch, validate_repo_url

router = APIRouter()


@router.post("/{repo_id}/analyze", response_model=AnalysisRunResponse)
def analyze_repository(
    repo_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Inicia el análisis de un repositorio clonándolo temporalmente.

    - Estudiantes solo pueden analizar sus propios repositorios.
    - Profesores pueden analizar repositorios de proyectos que ellos crearon.
    """
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repositorio no encontrado")

    # ── Autorización ──────────────────────────────────────────────
    if current_user.role == UserRole.STUDENT and repo.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="No puedes analizar este repositorio")

    if current_user.role in (UserRole.PROFESSOR, UserRole.ADMIN):
        project = db.query(Project).filter(
            Project.id == repo.project_id,
            Project.professor_id == current_user.id,
        ).first()
        if not project:
            raise HTTPException(status_code=403, detail="No puedes analizar este repositorio")

    # ── Evitar análisis concurrente ───────────────────────────────
    if repo.status == RepositoryStatus.ANALYZING:
        raise HTTPException(status_code=409, detail="Ya hay un análisis en curso")

    # ── Validaciones de seguridad ─────────────────────────────────
    validated_url = validate_repo_url(repo.repo_url)
    validated_branch = validate_branch(repo.branch)

    # ── Crear registro de ejecución ───────────────────────────────
    analysis_run = AnalysisRun(
        repository_id=repo.id,
        status=AnalysisRunStatus.PENDING,
    )
    db.add(analysis_run)

    repo.status = RepositoryStatus.ANALYZING
    db.commit()
    db.refresh(analysis_run)

    # ── Clonar y analizar ─────────────────────────────────────────
    repo_path: str | None = None
    try:
        repo_path = clone_repository(validated_url, validated_branch)

        analysis_run.status = AnalysisRunStatus.RUNNING
        analysis_run.started_at = datetime.now(timezone.utc)
        db.commit()

        # Leer commit hash del HEAD clonado
        cloned = git.Repo(repo_path)
        commit_hash = cloned.head.commit.hexsha

        analysis_run.commit_hash = commit_hash
        repo.last_commit_hash = commit_hash
        repo.last_analyzed_at = datetime.now(timezone.utc)

        analysis_run.status = AnalysisRunStatus.COMPLETED
        analysis_run.finished_at = datetime.now(timezone.utc)
        repo.status = RepositoryStatus.ANALYZED

        db.commit()
        db.refresh(analysis_run)

    except (CloneError, Exception) as exc:
        db.rollback()

        analysis_run.status = AnalysisRunStatus.FAILED
        analysis_run.error_message = str(exc)
        analysis_run.finished_at = datetime.now(timezone.utc)
        repo.status = RepositoryStatus.FAILED

        db.commit()
        db.refresh(analysis_run)

        raise HTTPException(status_code=422, detail=str(exc))
    finally:
        if repo_path:
            cleanup_repo(repo_path)

    return analysis_run
