from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.auth import get_current_user
from app.db.deps import get_db
from app.models.analysis_run import AnalysisRun
from app.models.project import Project
from app.models.repository import Repository
from app.models.user import User, UserRole
from app.schemas.analysis_run import AnalysisRunResponse

router = APIRouter()


@router.get("/{analysis_run_id}", response_model=AnalysisRunResponse)
def get_analysis_run(
    analysis_run_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retorna un AnalysisRun validando permisos.

    - Estudiante: solo si es el dueño del repositorio asociado.
    - Profesor: solo si el repositorio pertenece a uno de sus proyectos.
    - Admin: cualquier análisis.
    """
    analysis_run = db.query(AnalysisRun).filter(AnalysisRun.id == analysis_run_id).first()
    if not analysis_run:
        raise HTTPException(status_code=404, detail="Analisis no encontrado")

    repo = db.query(Repository).filter(Repository.id == analysis_run.repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repositorio asociado no encontrado")

    if current_user.role == UserRole.STUDENT:
        if repo.student_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tienes acceso a este analisis")
    elif current_user.role == UserRole.PROFESSOR:
        project = db.query(Project).filter(
            Project.id == repo.project_id,
            Project.professor_id == current_user.id,
        ).first()
        if not project:
            raise HTTPException(status_code=403, detail="No tienes acceso a este analisis")
    # ADMIN puede ver cualquier análisis

    return analysis_run