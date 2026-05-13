import json
import re
from pathlib import Path
from typing import Any


MAX_FILE_SIZE = 1_000_000

LANGUAGE_UNKNOWN = "unknown"
FRAMEWORK_UNKNOWN = "unknown"


def analyze_structure(repo_path: str) -> dict:
    """Analiza la estructura basica de un repositorio clonado."""
    root = Path(repo_path)
    warnings: list[str] = []

    package_json = _find_root_file(root, "package.json")
    requirements_txt = _find_root_file(root, "requirements.txt")
    pyproject_toml = _find_root_file(root, "pyproject.toml")
    pipfile = _find_root_file(root, "pipfile")
    composer_json = _find_root_file(root, "composer.json")
    pipfile_dependencies = _read_pipfile_dependency_names(pipfile, warnings)

    language = _detect_language(
        package_json=package_json,
        requirements_txt=requirements_txt,
        pyproject_toml=pyproject_toml,
        pipfile=pipfile,
        composer_json=composer_json,
    )

    dependencies: list[str] = []
    dependencies.extend(_read_package_dependencies(package_json, warnings))
    dependencies.extend(_read_requirements_dependencies(requirements_txt, warnings))
    dependencies.extend(_read_pyproject_dependencies(pyproject_toml, warnings))
    dependencies.extend(_read_composer_dependencies(composer_json, warnings))
    dependencies = _unique_sorted(dependencies)

    return {
        "language": language,
        "framework": _detect_framework(language, dependencies + pipfile_dependencies),
        "dependencies": dependencies,
        "has_readme": _has_readme(root),
        "warnings": warnings,
    }


def _detect_language(
    *,
    package_json: Path | None,
    requirements_txt: Path | None,
    pyproject_toml: Path | None,
    pipfile: Path | None,
    composer_json: Path | None,
) -> str:
    if package_json:
        return "javascript"
    if requirements_txt or pyproject_toml or pipfile:
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
        for framework in ("fastapi", "django"):
            if framework in names:
                return framework

    if language == "php" and any("laravel" in name for name in names):
        return "laravel"

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

        name = re.split(r"\s*(?:==|>=|<=|~=|!=|>|<|=|\[)", line, maxsplit=1)[0].strip()
        if name:
            dependencies.append(name)

    return dependencies


def _read_pyproject_dependencies(path: Path | None, warnings: list[str]) -> list[str]:
    content = _read_text(path, warnings)
    if content is None:
        return []

    dependencies: list[str] = []
    dependencies.extend(_names_from_quoted_dependency_arrays(content))
    dependencies.extend(_names_from_toml_section(content, "tool.poetry.dependencies"))
    dependencies = [name for name in dependencies if name.lower() != "python"]

    return dependencies


def _read_pipfile_dependency_names(path: Path | None, warnings: list[str]) -> list[str]:
    content = _read_text(path, warnings)
    if content is None:
        return []

    dependencies: list[str] = []
    dependencies.extend(_names_from_toml_section(content, "packages"))
    dependencies.extend(_names_from_toml_section(content, "dev-packages"))

    return dependencies


def _read_composer_dependencies(path: Path | None, warnings: list[str]) -> list[str]:
    if not path:
        return []

    data = _read_json(path, warnings)
    if not isinstance(data, dict):
        return []

    dependencies: list[str] = []
    for key in ("require", "require-dev"):
        section = data.get(key)
        if isinstance(section, dict):
            dependencies.extend(_simple_composer_name(str(name)) for name in section.keys())

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


def _names_from_dependency_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []

    dependencies: list[str] = []
    for item in value:
        if not isinstance(item, str):
            continue
        name = re.split(r"\s*(?:==|>=|<=|~=|!=|>|<|=|\[)", item, maxsplit=1)[0].strip()
        if name:
            dependencies.append(name)

    return dependencies


def _names_from_quoted_dependency_arrays(content: str) -> list[str]:
    dependencies: list[str] = []
    array_pattern = re.compile(r"dependencies\s*=\s*\[(.*?)\]", re.IGNORECASE | re.DOTALL)

    for match in array_pattern.finditer(content):
        quoted_values = re.findall(r"""["']([^"']+)["']""", match.group(1))
        dependencies.extend(_names_from_dependency_list(quoted_values))

    return dependencies


def _names_from_toml_section(content: str, section_name: str) -> list[str]:
    dependencies: list[str] = []
    current_section: str | None = None

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        section_match = re.match(r"\[([^\]]+)\]", line)
        if section_match:
            current_section = section_match.group(1).strip().lower()
            continue

        if current_section != section_name.lower() or "=" not in line:
            continue

        name = line.split("=", maxsplit=1)[0].strip().strip("\"'")
        if name:
            dependencies.append(name)

    return dependencies


def _simple_composer_name(name: str) -> str:
    if "/" not in name:
        return name

    vendor, package = name.split("/", maxsplit=1)
    if vendor.lower() == "laravel":
        return "laravel"
    return package


def _unique_sorted(values: list[str]) -> list[str]:
    normalized = {value.strip().lower() for value in values if value.strip()}
    return sorted(normalized)
