import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import SUPABASE_JWT_SECRET
from app.db.deps import get_db
from app.models.user import User

security = HTTPBearer()


def get_token_payload(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    """Valida el token JWT de Supabase y retorna el payload decodificado.

    Lanza HTTPException 401 si el token falta, está expirado o es inválido.
    """
    token = credentials.credentials

    if not token:
        raise HTTPException(status_code=401, detail="Token no proporcionado")

    try:
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

    return payload


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
