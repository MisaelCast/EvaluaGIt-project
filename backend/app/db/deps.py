from app.db.database import SessionLocal


def get_db():
    """Patrón de dependencia de FastAPI: abre y cierra sesión de SQLAlchemy por petición."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
