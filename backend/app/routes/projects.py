from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.auth import get_current_user
from app.db.deps import get_db
from app.models.project import Project
from app.models.user import User, UserRole
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter()


def _require_professor(user: User) -> None:
    if user.role not in (UserRole.PROFESSOR, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Solo profesores pueden gestionar proyectos")


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_professor(current_user)
    return db.query(Project).filter(Project.professor_id == current_user.id).all()


@router.post("", response_model=ProjectResponse)
def create_project(
    body: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_professor(current_user)

    project = Project(
        professor_id=current_user.id,
        **body.model_dump(),
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_professor(current_user)

    project = db.query(Project).filter(
        Project.id == project_id,
        Project.professor_id == current_user.id,
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str,
    body: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_professor(current_user)

    project = db.query(Project).filter(
        Project.id == project_id,
        Project.professor_id == current_user.id,
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_professor(current_user)

    project = db.query(Project).filter(
        Project.id == project_id,
        Project.professor_id == current_user.id,
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    db.delete(project)
    db.commit()
