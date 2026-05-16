from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.auth import get_current_user
from app.db.deps import get_db
from app.models.project import Project
from app.models.repository import Repository, RepositoryStatus
from app.models.user import User, UserRole
from app.schemas.repository import RepositoryCreate, RepositoryResponse

router = APIRouter()


@router.post("", response_model=RepositoryResponse)
def create_repository(
    body: RepositoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == body.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    if current_user.role == UserRole.PROFESSOR and project.professor_id != current_user.id:
        raise HTTPException(status_code=403, detail="No puedes vincular repositorios a este proyecto")

    existing = db.query(Repository).filter(
        Repository.student_id == current_user.id,
        Repository.project_id == body.project_id,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Ya tienes un repositorio vinculado a este proyecto")

    # MVP: usamos student_id para el usuario actual aunque sea profesor/admin,
    # para permitir probar el análisis sin implementar alumnos todavía.
    repo = Repository(
        project_id=body.project_id,
        student_id=current_user.id,
        repo_url=body.repo_url,
        branch=body.branch,
        status=RepositoryStatus.LINKED,
    )
    db.add(repo)
    db.commit()
    db.refresh(repo)
    return repo


@router.get("/mine", response_model=list[RepositoryResponse])
def list_my_repositories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Repository).filter(Repository.student_id == current_user.id).all()


@router.get("/projects/{project_id}/repositories", response_model=list[RepositoryResponse])
def list_project_repositories(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role not in (UserRole.PROFESSOR, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Solo profesores pueden ver repositorios del proyecto")

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    if current_user.role == UserRole.PROFESSOR and project.professor_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este proyecto")

    return db.query(Repository).filter(Repository.project_id == project_id).all()


@router.get("/{repo_id}", response_model=RepositoryResponse)
def get_repository(
    repo_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retorna un repositorio validando permisos:

    - Estudiante: solo si es el dueño del repo.
    - Profesor: solo si el repo pertenece a uno de sus proyectos.
    - Admin: cualquier repositorio.
    """
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repositorio no encontrado")

    if current_user.role == UserRole.STUDENT and repo.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este repositorio")

    if current_user.role == UserRole.PROFESSOR:
        project = db.query(Project).filter(
            Project.id == repo.project_id,
            Project.professor_id == current_user.id,
        ).first()
        if not project:
            raise HTTPException(status_code=403, detail="No tienes acceso a este repositorio")

    return repo


@router.delete("/{repo_id}", status_code=204)
def delete_repository(
    repo_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repositorio no encontrado")

    if current_user.role == UserRole.STUDENT and repo.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="No puedes eliminar este repositorio")

    if current_user.role == UserRole.PROFESSOR:
        project = db.query(Project).filter(
            Project.id == repo.project_id,
            Project.professor_id == current_user.id,
        ).first()
        if not project:
            raise HTTPException(status_code=403, detail="No puedes eliminar este repositorio")

    db.delete(repo)
    db.commit()
