import shutil
import uuid
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from pathlib import Path

import git


class CloneError(Exception):
    """Error controlado durante el clonado de un repositorio."""

    pass


def clone_repository(repo_url: str, branch: str) -> str:
    """Clona un repositorio Git en un directorio temporal.

    Args:
        repo_url: URL ya validada de GitHub (debe provenir de validate_repo_url).
        branch: Nombre de la rama ya validado.

    Returns:
        Ruta absoluta del directorio clonado.

    Raises:
        CloneError: Si ocurre un error de clonado o se excede el timeout.
    """
    target_path = Path("/tmp/repos") / str(uuid.uuid4())
    target_path.mkdir(parents=True, exist_ok=True)

    def _clone():
        git.Repo.clone_from(
            url=repo_url,
            to_path=str(target_path),
            branch=branch,
            depth=100,  # descargamos los commits más recientes para análisis, pero no todo el historial
            single_branch=True,
        )

    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_clone)
            future.result(timeout=30)
    except TimeoutError:
        cleanup_repo(str(target_path))
        raise CloneError("El clonado excedió el tiempo máximo de 30 segundos")
    except git.GitCommandError as exc:
        cleanup_repo(str(target_path))
        raise CloneError(f"Error al clonar el repositorio: {exc}")

    return str(target_path)


def cleanup_repo(path: str) -> None:
    """Elimina el directorio clonado si existe.

    Es seguro llamarla múltiples veces; no falla si el directorio ya fue borrado.
    """
    if path and Path(path).exists():
        shutil.rmtree(path, ignore_errors=True)
