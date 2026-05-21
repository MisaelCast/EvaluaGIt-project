import shutil
import subprocess
import uuid
from pathlib import Path


DOLOS_IMAGE = "ghcr.io/dodona-edu/dolos-cli:latest"
DOLOS_WORKDIR = "/tmp/dolos"


class DolosError(Exception):
    pass


def check_docker_available() -> bool:
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
    except (FileNotFoundError, OSError):
        return False

    return result.returncode == 0


def check_dolos_image_available() -> bool:
    try:
        result = subprocess.run(
            ["docker", "image", "inspect", DOLOS_IMAGE],
            capture_output=True,
            text=True,
            check=False,
        )
    except (FileNotFoundError, OSError):
        return False

    return result.returncode == 0


def get_dolos_status() -> dict[str, bool | str]:
    docker_available = check_docker_available()
    image_available = check_dolos_image_available() if docker_available else False

    return {
        "docker_available": docker_available,
        "image": DOLOS_IMAGE,
        "image_available": image_available,
        "ready": docker_available and image_available,
    }


def prepare_dolos_workspace(project_id: str) -> str:
    workspace = Path(DOLOS_WORKDIR) / f"{project_id}-{uuid.uuid4()}"
    workspace.mkdir(parents=True, exist_ok=False)
    return str(workspace)


def cleanup_dolos_workspace(path: str) -> None:
    shutil.rmtree(path, ignore_errors=True)
