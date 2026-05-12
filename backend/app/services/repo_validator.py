import re
import urllib.parse


def validate_repo_url(url: str) -> str:
    """Valida que la URL sea un repositorio público de GitHub.

    Acepta formatos:
      - https://github.com/{owner}/{repo}
      - https://github.com/{owner}/{repo}.git

    Rechaza cualquier otro dominio, IP, localhost o esquemas no HTTPS.
    """
    parsed = urllib.parse.urlparse(url.strip())

    if parsed.scheme != "https":
        raise ValueError("La URL debe usar el esquema https://")

    if parsed.hostname != "github.com":
        raise ValueError("Solo se permiten repositorios hospedados en github.com")

    # Limpiar posible .git al final
    path = parsed.path.removesuffix(".git")

    # Debe tener exactamente /owner/repo (2 segmentos)
    parts = [p for p in path.split("/") if p]
    if len(parts) != 2:
        raise ValueError(
            "Formato inválido. Se espera: https://github.com/{owner}/{repo}"
        )

    owner, repo = parts
    if not owner or not repo:
        raise ValueError("Owner y nombre del repositorio no pueden estar vacíos")

    # Construir URL limpia sin .git ni query ni fragment
    clean_url = f"https://github.com/{owner}/{repo}"
    return clean_url


def validate_branch(branch: str) -> str:
    """Valida que el nombre de rama sea seguro.

    Reglas:
      - Máximo 100 caracteres.
      - Solo letras, números, punto, guión, guión bajo y slash.
    """
    if len(branch) > 100:
        raise ValueError("El nombre de la rama no puede exceder 100 caracteres")

    if not re.match(r"^[a-zA-Z0-9._/-]+$", branch):
        raise ValueError(
            "El nombre de la rama contiene caracteres no permitidos. "
            "Solo se admiten letras, números, punto, guión, guión bajo y slash."
        )

    return branch
