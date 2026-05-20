from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.auth import get_current_user
from app.db.deps import get_db
from app.models.analysis_run import AnalysisRun
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.repository import Repository
from app.models.user import User, UserRole
from app.schemas.project import JoinProjectRequest, ProjectCreate, ProjectResponse, ProjectUpdate
from app.schemas.repository import RepositoryResponse
from app.services.join_code import generate_join_code

router = APIRouter()


def _require_professor(user: User) -> None:
    """Helper que rechaza la petición si el usuario no es PROFESSOR ni ADMIN."""
    if user.role not in (UserRole.PROFESSOR, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Solo profesores pueden gestionar proyectos")


def _create_unique_join_code(db: Session) -> str:
    """Genera un join_code único, reintentando si hay colisión."""
    for _ in range(5):
        code = generate_join_code()
        existing = db.query(Project).filter(Project.join_code == code).first()
        if not existing:
            return code
    raise RuntimeError("No se pudo generar código de unión")


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_professor(current_user)
    return db.query(Project).filter(Project.professor_id == current_user.id).all()


@router.post("/join", response_model=ProjectResponse)
def join_project(
    body: JoinProjectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Solo alumnos pueden unirse a proyectos")

    code = body.join_code.strip().upper()
    project = db.query(Project).filter(Project.join_code == code).first()
    if not project:
        raise HTTPException(status_code=404, detail="Codigo de proyecto invalido")

    existing = db.query(ProjectMember).filter(
        ProjectMember.project_id == project.id,
        ProjectMember.user_id == current_user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Ya estas unido a este proyecto")

    member = ProjectMember(
        project_id=project.id,
        user_id=current_user.id,
        role="STUDENT",
    )
    db.add(member)
    db.commit()
    db.refresh(project)
    return project


@router.get("/joined", response_model=list[ProjectResponse])
def list_joined_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Solo alumnos pueden consultar proyectos unidos")

    members = db.query(ProjectMember).filter(
        ProjectMember.user_id == current_user.id,
        ProjectMember.role == "STUDENT",
    ).all()

    project_ids = [m.project_id for m in members]
    if not project_ids:
        return []

    return db.query(Project).filter(Project.id.in_(project_ids)).all()


@router.post("", response_model=ProjectResponse)
def create_project(
    body: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_professor(current_user)

    join_code = _create_unique_join_code(db)

    project = Project(
        professor_id=current_user.id,
        join_code=join_code,
        **body.model_dump(),
    )
    db.add(project)
    db.flush()

    member = ProjectMember(
        project_id=project.id,
        user_id=current_user.id,
        role="PROFESSOR",
    )
    db.add(member)
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

    repos = db.query(Repository).filter(Repository.project_id == project_id).all()
    for repo in repos:
        db.query(AnalysisRun).filter(AnalysisRun.repository_id == repo.id).delete()

    db.query(Repository).filter(Repository.project_id == project_id).delete()
    db.query(ProjectMember).filter(ProjectMember.project_id == project_id).delete()
    db.delete(project)
    db.commit()


@router.get("/{project_id}/repositories", response_model=list[RepositoryResponse])
def list_project_repositories(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista todos los repositorios vinculados a un proyecto del profesor autenticado."""
    _require_professor(current_user)

    project = db.query(Project).filter(
        Project.id == project_id,
        Project.professor_id == current_user.id,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    return db.query(Repository).filter(Repository.project_id == project_id).all()
