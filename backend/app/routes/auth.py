from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.user import User, UserRole
from app.schemas.user import SyncUserRequest, UserResponse

router = APIRouter()


@router.post("/sync-user", response_model=UserResponse)
def sync_user(body: SyncUserRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.supabase_id == body.supabase_id).first()

    if user:
        user.email = body.email
        user.full_name = body.full_name
        user.avatar_url = body.avatar_url
    else:
        user = User(
            supabase_id=body.supabase_id,
            email=body.email,
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
def get_me(supabase_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.supabase_id == supabase_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return user
