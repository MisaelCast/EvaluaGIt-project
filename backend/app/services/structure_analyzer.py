import json
import re
from pathlib import Path
from typing import Any


MAX_FILE_SIZE = 1_000_000

LANGUAGE_UNKNOWN = "unknown"
FRAMEWORK_UNKNOWN = "unknown"


def analyze_structure(repo_path: str, requirements: dict | None = None) -> dict:
    """Analiza la estructura basica de un repositorio clonado."""
    root = Path(repo_path)
    warnings: list[str] = []
    requirements = _safe_requirements(requirements, warnings)

    package_json = _find_root_file(root, "package.json")
    requirements_txt = _find_root_file(root, "requirements.txt")
    composer_json = _find_root_file(root, "composer.json")

    language = _detect_language(
        package_json=package_json,
        requirements_txt=requirements_txt,
        composer_json=composer_json,
    )

    dependencies: list[str] = []
    dependencies.extend(_read_package_dependencies(package_json, warnings))
    dependencies.extend(_read_requirements_dependencies(requirements_txt, warnings))
    dependencies = _unique_sorted(dependencies)

    required_files = _analyze_required_files(root, requirements, warnings)
    forbidden_files = _analyze_forbidden_files(root, requirements, warnings)
    score = _calculate_structure_score(required_files, forbidden_files)

    return {
        "language": language,
        "framework": _detect_framework(language, dependencies),
        "dependencies": dependencies,
        "has_readme": _has_readme(root),
        "required_files": required_files,
        "forbidden_files": forbidden_files,
        "score": {
            "structure": score,
        },
        "warnings": warnings,
    }


def _detect_language(
    *,
    package_json: Path | None,
    requirements_txt: Path | None,
    composer_json: Path | None,
) -> str:
    if package_json:
        return "javascript"
    if requirements_txt:
        return "python"
    if composer_json:
        return "php"
    return LANGUAGE_UNKNOWN


def _detect_framework(language: str, dependencies: list[str]) -> str:
    names = {dependency.lower() for dependency in dependencies}

    if language == "javascript":
        for framework in ("express", "vue", "react"):
            if framework in names:
                return framework

    if language == "python":
        if "fastapi" in names:
            return "fastapi"

    return FRAMEWORK_UNKNOWN


def _find_root_file(root: Path, expected_name: str) -> Path | None:
    expected = expected_name.lower()
    try:
        for child in root.iterdir():
            if child.is_file() and child.name.lower() == expected:
                return child
    except OSError:
        return None
    return None


def _has_readme(root: Path) -> bool:
    readme_names = {"readme", "readme.md", "readme.txt"}
    try:
        return any(
            child.is_file() and child.name.lower() in readme_names
            for child in root.iterdir()
        )
    except OSError:
        return False


def _safe_requirements(requirements: dict | None, warnings: list[str]) -> dict:
    if requirements is None:
        return {}
    if isinstance(requirements, dict):
        return requirements

    warnings.append("Formato de requerimientos invalido; se ignoraron las reglas")
    return {}


def _analyze_required_files(
    root: Path,
    requirements: dict,
    warnings: list[str],
) -> dict[str, list[str]]:
    found: list[str] = []
    missing: list[str] = []

    for raw_path in _safe_list(requirements.get("requiredFiles")):
        normalized = _normalize_relative_path(raw_path, warnings)
        if not normalized:
            continue

        if _path_exists_inside_repo(root, normalized):
            found.append(normalized)
        else:
            missing.append(normalized)

    return {
        "found": sorted(found),
        "missing": sorted(missing),
    }


def _analyze_forbidden_files(
    root: Path,
    requirements: dict,
    warnings: list[str],
) -> dict[str, list[str]]:
    found: set[str] = set()

    for raw_pattern in _safe_list(requirements.get("forbiddenFiles")):
        pattern = _normalize_relative_path(raw_pattern, warnings)
        if not pattern:
            continue

        for match in _glob_inside_repo(root, pattern, warnings):
            found.add(match)

    for path in sorted(found):
        warnings.append(f"Archivo prohibido detectado: {path}")

    return {
        "found": sorted(found),
    }


def _calculate_structure_score(
    required_files: dict[str, list[str]],
    forbidden_files: dict[str, list[str]],
) -> int:
    score = 100
    score -= len(required_files["missing"]) * 10
    score -= len(forbidden_files["found"]) * 20
    return max(score, 0)


def _safe_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    return []


def _normalize_relative_path(value: Any, warnings: list[str]) -> str | None:
    if not isinstance(value, str) or not value.strip():
        warnings.append(f"Path invalido ignorado: {value}")
        return None

    raw_path = value.strip().replace("\\", "/")
    path = Path(raw_path)

    # No se aceptan rutas absolutas ni traversal para evitar salir del repo.
    if path.is_absolute() or ".." in path.parts:
        warnings.append(f"Path inseguro ignorado: {value}")
        return None

    normalized = path.as_posix()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    if not normalized:
        warnings.append(f"Path invalido ignorado: {value}")
        return None

    return normalized


def _path_exists_inside_repo(root: Path, relative_path: str) -> bool:
    candidate = root / relative_path
    return _is_inside_repo(root, candidate) and candidate.exists()


def _glob_inside_repo(root: Path, pattern: str, warnings: list[str]) -> list[str]:
    matches: list[str] = []

    try:
        for path in root.glob(pattern):
            if not path.is_file() or not _is_inside_repo(root, path):
                continue
            matches.append(path.relative_to(root).as_posix())
    except (OSError, ValueError, RuntimeError) as exc:
        warnings.append(f"Patron invalido ignorado: {pattern} ({exc})")

    return matches


def _is_inside_repo(root: Path, candidate: Path) -> bool:
    try:
        candidate.resolve(strict=False).relative_to(root.resolve(strict=False))
        return True
    except ValueError:
        return False


def _read_package_dependencies(path: Path | None, warnings: list[str]) -> list[str]:
    if not path:
        return []

    data = _read_json(path, warnings)
    if not isinstance(data, dict):
        return []

    dependencies: list[str] = []
    for key in ("dependencies", "devDependencies"):
        section = data.get(key)
        if isinstance(section, dict):
            dependencies.extend(str(name) for name in section.keys())

    return dependencies


def _read_requirements_dependencies(path: Path | None, warnings: list[str]) -> list[str]:
    content = _read_text(path, warnings)
    if content is None:
        return []

    dependencies: list[str] = []
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith(("-", "--")):
            continue

        match = re.match(r"([A-Za-z0-9_.-]+)", line)
        if match:
            dependencies.append(match.group(1))

    return dependencies


def _read_json(path: Path, warnings: list[str]) -> Any:
    content = _read_text(path, warnings)
    if content is None:
        return None

    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        warnings.append(f"No se pudo parsear {path.name}: {exc}")
        return None


def _read_text(path: Path | None, warnings: list[str]) -> str | None:
    content = _read_bytes(path, warnings)
    if content is None:
        return None

    try:
        return content.decode("utf-8")
    except UnicodeDecodeError as exc:
        warnings.append(f"No se pudo leer {path.name}: {exc}")
        return None


def _read_bytes(path: Path | None, warnings: list[str]) -> bytes | None:
    if not path:
        return None

    try:
        if path.stat().st_size > MAX_FILE_SIZE:
            warnings.append(f"Archivo ignorado por exceder 1MB: {path.name}")
            return None
        return path.read_bytes()
    except OSError as exc:
        warnings.append(f"No se pudo leer {path.name}: {exc}")
        return None


def _unique_sorted(values: list[str]) -> list[str]:
    normalized = {value.strip().lower() for value in values if value.strip()}
    return sorted(normalized)
