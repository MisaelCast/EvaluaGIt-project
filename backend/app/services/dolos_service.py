import csv
import shutil
import subprocess
import uuid
from pathlib import Path


DOLOS_IMAGE = "ghcr.io/dodona-edu/dolos-cli:latest"
DOLOS_WORKDIR = "/tmp/dolos"
DOLOS_TIMEOUT_SECONDS = 120

IGNORED_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "vendor",
}
IGNORED_FILENAMES = {
    ".env",
    ".env.local",
    ".env.production",
    "secrets.json",
}
IGNORED_SUFFIXES = {
    ".crt",
    ".key",
    ".pem",
}
SOURCE_SUFFIXES = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".css",
    ".go",
    ".h",
    ".hpp",
    ".html",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".scala",
    ".sql",
    ".swift",
    ".ts",
    ".tsx",
    ".vue",
}


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


def _is_allowed_source_file(path: Path) -> bool:
    if path.name in IGNORED_FILENAMES:
        return False

    if path.suffix.lower() in IGNORED_SUFFIXES:
        return False

    return path.suffix.lower() in SOURCE_SUFFIXES


def prepare_dolos_submissions(
    workspace_path: str,
    cloned_repositories: list[dict],
) -> list[dict]:
    submissions_path = Path(workspace_path) / "submissions"
    submissions_path.mkdir(parents=True, exist_ok=True)

    prepared_submissions = []

    for item in cloned_repositories:
        source_path = Path(str(item["path"]))
        destination_path = submissions_path / str(item["repository_id"])
        copied_files = 0

        for file_path in source_path.rglob("*"):
            if not file_path.is_file():
                continue

            relative_path = file_path.relative_to(source_path)
            if any(part in IGNORED_DIRS for part in relative_path.parts):
                continue

            if not _is_allowed_source_file(file_path):
                continue

            target_path = destination_path / relative_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, target_path)
            copied_files += 1

        prepared_submissions.append(
            {
                "repository_id": str(item["repository_id"]),
                "student_id": str(item["student_id"]),
                "path": str(destination_path),
                "files_count": copied_files,
            }
        )

    return prepared_submissions


def run_dolos_analysis(workspace_path: str, repositories: list[dict] | None = None) -> dict:
    workspace = Path(workspace_path)
    submissions_path = workspace / "submissions"
    report_path = workspace / "report"
    input_files = sorted(path for path in submissions_path.rglob("*") if path.is_file())

    if len(input_files) < 2:
        raise DolosError("No hay suficientes archivos fuente para ejecutar Dolos")

    container_files = [
        f"/dolos/workspace/{path.relative_to(workspace).as_posix()}"
        for path in input_files
    ]
    command = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{workspace_path}:/dolos/workspace",
        "-w",
        "/dolos/workspace",
        DOLOS_IMAGE,
        "run",
        "--language",
        "char",
        "--output-format",
        "csv",
        "--output-destination",
        "/dolos/workspace/report",
        *container_files,
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=DOLOS_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise DolosError("Dolos excedio el tiempo maximo de ejecucion") from exc
    except (FileNotFoundError, OSError) as exc:
        raise DolosError("No se pudo iniciar Docker para ejecutar Dolos") from exc

    raw_output = "\n".join(part for part in (result.stdout, result.stderr) if part).strip()

    if result.returncode != 0:
        raise DolosError(raw_output or "Dolos termino con error")

    parsed_output = parse_dolos_output(workspace_path, repositories)

    return {
        "raw_output": raw_output[:6000] if raw_output else None,
        "pairs": parsed_output["pairs"],
        "output_files": parsed_output["output_files"],
        "summary": parsed_output["summary"],
    }


def _parse_similarity_value(value: str | None) -> float | None:
    if value in (None, ""):
        return None

    try:
        return float(value)
    except ValueError:
        return None


def _extract_submission_path(file_path: str) -> tuple[str | None, str]:
    marker = "/submissions/"
    normalized = file_path.replace("\\", "/")

    if marker in normalized:
        tail = normalized.split(marker, 1)[1]
    elif normalized.startswith("submissions/"):
        tail = normalized.removeprefix("submissions/")
    else:
        return None, normalized

    parts = [part for part in tail.split("/") if part]
    if not parts:
        return None, normalized

    repository_id = parts[0]
    relative_file = "/".join(parts[1:])
    return repository_id, relative_file


def _format_similarity_percent(similarity: float | None) -> float | None:
    if similarity is None:
        return None

    return round(similarity * 100, 1)


def _classify_similarity(similarity_percent: float) -> dict[str, str]:
    if similarity_percent >= 85:
        return {
            "level": "high",
            "label": "Similitud alta o muy sospechosa",
        }

    if similarity_percent >= 70:
        return {
            "level": "relevant",
            "label": "Similitud relevante",
        }

    if similarity_percent >= 50:
        return {
            "level": "review",
            "label": "Revisar solo si hay contexto",
        }

    return {
        "level": "normal",
        "label": "Coincidencia normal o irrelevante",
    }


def parse_dolos_output(workspace_path: str, repositories: list[dict] | None = None) -> dict:
    workspace = Path(workspace_path)
    report_path = workspace / "report"
    output_files = []
    pairs = []
    repository_map = {
        str(item["repository_id"]): item
        for item in repositories or []
    }
    summary: dict = {
        "files_generated": 0,
        "total_pairs_raw": 0,
        "total_pairs_between_submissions": 0,
        "normal_pairs_count": 0,
        "review_pairs_count": 0,
        "relevant_pairs_count": 0,
        "high_pairs_count": 0,
        "pairs_returned": 0,
    }

    if not report_path.exists():
        summary["message"] = "No se encontro la carpeta de salida de Dolos"
        return {
            "pairs": pairs,
            "output_files": output_files,
            "summary": summary,
        }

    output_files = [
        str(path.relative_to(workspace))
        for path in sorted(report_path.rglob("*"))
        if path.is_file()
    ]
    summary["files_generated"] = len(output_files)

    pairs_path = report_path / "pairs.csv"
    if not pairs_path.exists():
        summary["message"] = "No se encontro pairs.csv en la salida de Dolos"
        return {
            "pairs": pairs,
            "output_files": output_files,
            "summary": summary,
        }

    try:
        with pairs_path.open("r", encoding="utf-8", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                left = row.get("leftFilePath") or row.get("left") or ""
                right = row.get("rightFilePath") or row.get("right") or ""
                similarity = _parse_similarity_value(row.get("similarity"))
                left_repository_id, left_file = _extract_submission_path(left)
                right_repository_id, right_file = _extract_submission_path(right)

                summary["total_pairs_raw"] += 1

                if not left_repository_id or not right_repository_id:
                    continue

                if left_repository_id == right_repository_id:
                    continue

                summary["total_pairs_between_submissions"] += 1

                if similarity is None:
                    continue

                similarity_percent = _format_similarity_percent(similarity)
                if similarity_percent is None:
                    continue

                classification = _classify_similarity(similarity_percent)
                summary[f"{classification['level']}_pairs_count"] += 1

                pairs.append(
                    {
                        "left_repository_id": left_repository_id,
                        "right_repository_id": right_repository_id,
                        "left_student_name": repository_map.get(left_repository_id, {}).get("student_name", ""),
                        "right_student_name": repository_map.get(right_repository_id, {}).get("student_name", ""),
                        "left_file": left_file,
                        "right_file": right_file,
                        "similarity": similarity,
                        "similarity_percent": similarity_percent,
                        "level": classification["level"],
                        "label": classification["label"],
                        "extra": dict(row),
                    }
                )
    except (OSError, csv.Error, UnicodeDecodeError):
        summary["message"] = "No se pudo leer pairs.csv de Dolos"
        return {
            "pairs": [],
            "output_files": output_files,
            "summary": summary,
        }

    important_pairs = [
        pair
        for pair in pairs
        if pair["level"] in {"high", "relevant"}
    ]
    review_pairs = [
        pair
        for pair in pairs
        if pair["level"] == "review"
    ]

    if important_pairs:
        pairs = important_pairs
    elif review_pairs:
        pairs = review_pairs

    pairs.sort(key=lambda pair: pair["similarity_percent"], reverse=True)
    pairs = pairs[:10]
    summary["pairs_returned"] = len(pairs)

    if not pairs:
        summary["message"] = "Dolos no encontro pares entre entregas diferentes"

    return {
        "pairs": pairs,
        "output_files": output_files,
        "summary": summary,
    }
