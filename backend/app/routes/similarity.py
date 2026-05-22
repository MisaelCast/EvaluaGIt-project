from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.auth import get_current_user
from app.db.deps import get_db
from app.models.project import Project
from app.models.repository import Repository
from app.models.similarity_run import SimilarityRun
from app.models.user import User, UserRole
from app.schemas.similarity import (
    SimilarityAnalysisResponse,
    SimilarityRepositoryItem,
    SimilarityRunResponse,
)
from app.services.clone_service import CloneError, cleanup_repo, clone_repository
from app.services.dolos_service import (
    DolosError,
    cleanup_dolos_workspace,
    get_dolos_status,
    prepare_dolos_submissions,
    prepare_dolos_workspace,
    run_dolos_analysis,
)
from app.services.repo_validator import validate_branch, validate_repo_url

router = APIRouter()

SIMILARITY_STATUS_PENDING = "PENDING"
SIMILARITY_STATUS_RUNNING = "RUNNING"
SIMILARITY_STATUS_COMPLETED = "COMPLETED"
SIMILARITY_STATUS_FAILED = "FAILED"


def _get_authorized_project(
    project_id: UUID,
    current_user: User,
    db: Session,
) -> Project:
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

    return project


@router.get("/similarity/dolos/status")
def get_similarity_dolos_status(
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in (UserRole.PROFESSOR, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="No puedes consultar el estado de Dolos")

    return get_dolos_status()


@router.post(
    "/projects/{project_id}/similarity/analyze",
    response_model=SimilarityRunResponse,
)
def prepare_similarity_analysis(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = _get_authorized_project(project_id, current_user, db)

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

    similarity_run = SimilarityRun(
        project_id=project.id,
        status=SIMILARITY_STATUS_PENDING,
    )
    db.add(similarity_run)
    db.commit()
    db.refresh(similarity_run)

    workspace_path = ""
    cloned_paths: list[str] = []

    try:
        similarity_run.status = SIMILARITY_STATUS_RUNNING
        similarity_run.started_at = datetime.utcnow()
        db.commit()

        dolos_status = get_dolos_status()
        if not dolos_status["ready"]:
            raise HTTPException(status_code=422, detail="Dolos no esta listo para ejecutarse")

        workspace_path = prepare_dolos_workspace(str(project.id))
        cloned_repositories = []

        for repo, user in repos_with_users:
            try:
                repo_url = validate_repo_url(repo.repo_url)
                branch = validate_branch(repo.branch)
                cloned_path = clone_repository(repo_url, branch)
            except (ValueError, CloneError) as exc:
                raise HTTPException(
                    status_code=422,
                    detail="No se pudo clonar una de las entregas",
                ) from exc

            cloned_paths.append(cloned_path)
            cloned_repositories.append(
                {
                    "repository_id": str(repo.id),
                    "student_id": str(user.id),
                    "student_name": user.full_name,
                    "student_email": user.email,
                    "repo_url": repo.repo_url,
                    "branch": repo.branch,
                    "path": cloned_path,
                }
            )

        prepare_dolos_submissions(workspace_path, cloned_repositories)
        dolos_result = run_dolos_analysis(workspace_path, cloned_repositories)

        result = SimilarityAnalysisResponse(
            project_id=str(project.id),
            status="COMPLETED",
            message="Analisis de similitud ejecutado con Dolos",
            repositories_count=len(repositories),
            repositories=repositories,
            pairs=dolos_result.get("pairs", []),
            executed=True,
            raw_output=dolos_result.get("raw_output"),
            output_files=dolos_result.get("output_files", []),
            summary=dolos_result.get("summary"),
        )

        similarity_run.result_json = result.model_dump(mode="json")
        similarity_run.status = SIMILARITY_STATUS_COMPLETED
        similarity_run.finished_at = datetime.utcnow()
        db.commit()
        db.refresh(similarity_run)
        return similarity_run
    except HTTPException as exc:
        db.rollback()
        similarity_run.status = SIMILARITY_STATUS_FAILED
        similarity_run.error_message = str(exc.detail)
        similarity_run.finished_at = datetime.utcnow()
        db.commit()
        raise
    except DolosError as exc:
        db.rollback()
        similarity_run.status = SIMILARITY_STATUS_FAILED
        similarity_run.error_message = "No se pudo ejecutar Dolos"
        similarity_run.finished_at = datetime.utcnow()
        db.commit()
        raise HTTPException(status_code=500, detail="No se pudo ejecutar Dolos") from exc
    except Exception as exc:
        db.rollback()
        similarity_run.status = SIMILARITY_STATUS_FAILED
        similarity_run.error_message = "No se pudo completar el analisis de similitud"
        similarity_run.finished_at = datetime.utcnow()
        db.commit()
        raise HTTPException(
            status_code=500,
            detail="No se pudo completar el analisis de similitud",
        ) from exc
    finally:
        for path in cloned_paths:
            cleanup_repo(path)

        if workspace_path:
            cleanup_dolos_workspace(workspace_path)


@router.get(
    "/projects/{project_id}/similarity/latest",
    response_model=SimilarityRunResponse,
)
def get_latest_similarity_analysis(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = _get_authorized_project(project_id, current_user, db)

    similarity_run = (
        db.query(SimilarityRun)
        .filter(SimilarityRun.project_id == project.id)
        .order_by(SimilarityRun.created_at.desc())
        .first()
    )
    if not similarity_run:
        raise HTTPException(
            status_code=404,
            detail="No hay analisis de similitud para este proyecto",
        )

    return similarity_run
