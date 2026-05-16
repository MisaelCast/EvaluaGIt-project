from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import httpx
from sqlalchemy.orm import Session

from app.core.config import SUPABASE_ANON_KEY, SUPABASE_URL
from app.db.deps import get_db
from app.models.user import User

security = HTTPBearer(auto_error=False)


def get_token_payload(
    credentials: HTTPAuthorizationCredentials | None = Security(security),
) -> dict:
    """Valida el token con Supabase Auth y retorna un payload compatible.

    Lanza HTTPException 401 si el token falta o Supabase no lo valida.
    """
    if credentials is None:
        raise HTTPException(status_code=401, detail="Token no proporcionado")

    token = credentials.credentials

    if not token:
        raise HTTPException(status_code=401, detail="Token no proporcionado")

    try:
        response = httpx.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={
                "Authorization": f"Bearer {token}",
                "apikey": SUPABASE_ANON_KEY,
            },
            timeout=10,
        )
    except httpx.RequestError:
        raise HTTPException(status_code=401, detail="No se pudo validar el token")

    if response.status_code in (401, 403):
        raise HTTPException(status_code=401, detail="Token inválido")
    if response.is_error:
        raise HTTPException(status_code=401, detail="No se pudo validar el token")

    try:
        data = response.json()
    except ValueError:
        raise HTTPException(status_code=401, detail="No se pudo validar el token")

    supabase_id = data.get("id")
    if not supabase_id:
        raise HTTPException(status_code=401, detail="Token sin identidad de usuario")

    return {
        "sub": supabase_id,
        "email": data.get("email"),
        "user_metadata": data.get("user_metadata", {}),
    }


def get_current_user(
    payload: dict = Depends(get_token_payload),
    db: Session = Depends(get_db),
) -> User:
    """Busca el usuario en la base de datos usando el supabase_id del JWT.

    Lanza HTTPException 401 si el usuario no existe localmente.
    """
    supabase_id = payload.get("sub")
    if not supabase_id:
        raise HTTPException(status_code=401, detail="Token sin identidad de usuario")

    user = db.query(User).filter(User.supabase_id == supabase_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    return user
