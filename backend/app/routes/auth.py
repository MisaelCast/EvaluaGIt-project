from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.auth import get_current_user, get_token_payload
from app.db.deps import get_db
from app.models.user import User, UserRole
from app.schemas.user import SyncUserRequest, UserResponse

router = APIRouter()


@router.post("/sync-user", response_model=UserResponse)
def sync_user(
    body: SyncUserRequest,
    payload: dict = Depends(get_token_payload),
    db: Session = Depends(get_db),
):
    """Crea o actualiza el usuario local a partir del JWT de Supabase.

    La identidad (supabase_id y email) se extrae del token validado,
    no del body. Solo full_name y avatar_url vienen del body.
    """
    supabase_id = payload.get("sub")
    if not supabase_id:
        raise HTTPException(status_code=401, detail="Token sin identidad de usuario")

    # El email verdadero viene del JWT, no del body
    email = payload.get("email") or body.email

    user = db.query(User).filter(User.supabase_id == supabase_id).first()

    if user:
        user.email = email
        user.full_name = body.full_name
        user.avatar_url = body.avatar_url
    else:
        user = User(
            supabase_id=supabase_id,
            email=email,
            full_name=body.full_name,
            avatar_url=body.avatar_url,
            role=UserRole.STUDENT,
        )
        db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError as exc:
        db.rollback()
        error_msg = str(exc.orig) if exc.orig else ""
        if "email" in error_msg.lower() or "users_email_key" in error_msg.lower():
            raise HTTPException(
                status_code=409,
                detail="Conflicto de datos: el email ya está registrado por otro usuario",
            )
        raise HTTPException(
            status_code=409,
            detail="Conflicto de datos: violación de constraint único",
        )

    return user


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Retorna el perfil del usuario autenticado desde la base de datos local."""
    return current_user
