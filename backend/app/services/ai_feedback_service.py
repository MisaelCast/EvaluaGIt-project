import json
import os
from pathlib import Path

import httpx

from app.core.config import GEMINI_API_KEY

GEMINI_MODEL = "gemini-2.5-flash-lite"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

VALID_RISK_LEVELS = {"low", "medium", "high", "critical"}
VALID_SEVERITIES = {"low", "medium", "high", "critical"}
VALID_CATEGORIES = {
    "security",
    "architecture",
    "maintainability",
    "performance",
    "validation",
    "cleanup",
    "readability",
}

IGNORED_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".next",
    ".nuxt",
    "vendor",
    "coverage",
    ".turbo",
}

IGNORED_FILES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    "secrets.json",
    "credentials.json",
}

IGNORED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".webp",
    ".mp4",
    ".webm",
    ".avi",
    ".mov",
    ".mp3",
    ".wav",
    ".ogg",
    ".pdf",
    ".zip",
    ".rar",
    ".7z",
    ".tar",
    ".gz",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".p12",
    ".pfx",
    ".pem",
    ".key",
    ".crt",
    ". CSR",
    ".lock",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
}

CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".vue",
    ".jsx",
    ".tsx",
    ".php",
    ".java",
    ".cs",
    ".go",
    ".rb",
    ".html",
    ".css",
    ".scss",
    ".sass",
    ".less",
    ".sql",
    ".sh",
    ".bash",
    ".zsh",
    ".ps1",
    ".yaml",
    ".yml",
    ".toml",
    ".json",
    ".xml",
    ".md",
}

CONTEXT_FILES = {
    "README",
    "README.md",
    "README.txt",
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "composer.json",
    "Cargo.toml",
    "go.mod",
    "Gemfile",
    "Makefile",
    "Dockerfile",
    "docker-compose.yml",
    ".gitignore",
    ".dockerignore",
}


def collect_repo_code_context(repo_path: str) -> dict:
    root = Path(repo_path)
    files = []

    try:
        for item in root.rglob("*"):
            if item.is_dir():
                if item.name in IGNORED_DIRS or any(parent.name in IGNORED_DIRS for parent in item.parents):
                    continue
                continue

            if item.name in IGNORED_FILES:
                continue

            if any(item.name.endswith(ext) for ext in IGNORED_EXTENSIONS):
                continue

            if any(part in IGNORED_DIRS for part in item.parts):
                continue

            is_code = any(item.name.endswith(ext) for ext in CODE_EXTENSIONS)
            is_context = item.name in CONTEXT_FILES

            if not (is_code or is_context):
                continue

            if item.stat().st_size > 5_000_000:
                continue

            try:
                content = item.read_text(encoding="utf-8", errors="ignore")
                rel_path = item.relative_to(root).as_posix()
                files.append({
                    "path": rel_path,
                    "content": content,
                })
            except OSError:
                continue

    except OSError:
        pass

    return {"files": files}


def build_feedback_prompt(context: dict) -> str:
    file_count = len(context.get("files", []))

    files_md = []
    for f in context.get("files", []):
        files_md.append(f"# {f['path']}\n{f['content'][:8000]}")

    files_section = "\n\n".join(files_md) if files_md else "No se encontraron archivos."

    prompt = f"""Eres un revisor tecnico estricto pero prudente para proyectos academicos de software.

Objetivo:
Entrega retroalimentacion constructiva sobre calidad tecnica del codigo. No acuses plagio. No des calificaciones academicas.

Comportamiento esperado:
- Se breve y directo
- No escribas explicaciones largas
- No inventes informacion
- Usa solo el codigo proporcionado
- No afirmes como hecho absoluto algo que no tenga evidencia suficiente
- Cuando no tengas certeza usa lenguaje prudente como "aparentemente", "posiblemente", "podria" o "parece"
- Reporta solo problemas realmente importantes y utiles para mejorar el proyecto
- No reportes detalles menores si no afectan claramente el funcionamiento o mantenimiento del proyecto
- No es obligatorio devolver issues
- Si el proyecto esta bien estructurado puedes devolver 0 issues
- Si solo hay mejoras menores devuelve 1 o 2 issues como maximo
- Si el proyecto esta bien estructurado no fuerces problemas menores
- No llenes la lista de issues solo por completar
- Devuelve entre 0 y 3 issues normalmente
- No reportes problemas de estilo visual o CSS inline salvo que afecten claramente mantenimiento o funcionamiento
- No reportes detalles muy pequenos de implementacion si no afectan el flujo principal
- No reportes posibles problemas hipoteticos como medium si no hay evidencia clara
- Si una observacion es solo una preferencia de estilo no incluirla como issue
- No repitas el mismo problema varias veces
- Si varios archivos tienen el mismo problema agrupalos cuando tenga sentido

Enfocate solo en problemas que afecten claramente:
- Seguridad
- Funcionamiento
- Mantenibilidad importante
- Arquitectura
- Errores probables
- Codigo claramente innecesario
- Hardcodeos relevantes

No reportes recomendaciones genericas como:
- Mejorar documentacion
- Agregar logging
- Usar variables de entorno
- Agregar autenticacion

Incluye esas recomendaciones solo si son realmente importantes para el proyecto revisado.

Limites de tamano:
- summary maximo 500 caracteres
- maximo 3 strengths
- cada strength maximo 180 caracteres
- issues entre 0 y 3
- 3 issues es un maximo no una meta
- Para proyectos buenos se esperan 0 a 2 issues
- cada issue.description maximo 300 caracteres
- cada issue.suggestion maximo 220 caracteres
- maximo 2 suggestions
- cada suggestion maximo 220 caracteres

Reglas para summary:
- Debe ser breve y honesto
- Debe decir si el proyecto esta bien en general
- Debe mencionar solo el principal riesgo tecnico si existe
- No debe repetir toda la lista de issues
- No debe hacer introducciones largas

Reglas para issues:
- Cada issue debe tener severity, category, file, description y suggestion
- severity debe ser uno de: low, medium, high, critical
- critical solo para problemas graves y evidentes que exponen datos o rompen seguridad
- high solo para problemas claros que pueden romper el sistema o exponer informacion sensible
- medium para problemas relevantes de mantenimiento funcionamiento arquitectura o validacion
- medium debe usarse solo si el problema afecta mantenimiento funcionamiento arquitectura o validacion de forma clara
- low solo si aporta valor claro y no es una observacion trivial
- low debe usarse solo si aporta valor real
- Si un problema es muy menor no lo incluyas
- No incluyas issues low salvo que sean claramente utiles
- No incluyas issues low triviales
- No marques como high security riesgos hipoteticos
- Usa high o critical solo si hay evidencia clara de claves expuestas acceso publico a datos sensibles bypass claro de permisos subida publica sin restriccion ejecucion de codigo inyeccion SQL real o vulnerabilidad evidente
- Si un problema es de validacion comun no lo clasifiques como security a menos que haya riesgo de seguridad evidente
- Filtros sin validacion en un DataFrame normalmente es validation
- API sin autenticacion en un proyecto local academico normalmente no es high security por si sola
- URL hardcodeada normalmente es maintainability
- Logica grande dentro de una vista normalmente es maintainability
- category debe ser uno de: security, architecture, maintainability, performance, validation, cleanup, readability
- Cada issue debe incluir la ruta real del archivo relacionada al problema
- No inventes rutas
- Si no hay un archivo claro usa "multiple"
- Ejemplos de rutas validas: app/main.py, src/views/HomeView.vue, backend/app/services/auth.py

Reglas para suggestions:
- Deben complementar los issues
- No repitas lo mismo que ya aparece en issues
- Si no hay sugerencias importantes devuelve []

quality_score:
- Entero entre 0 y 100
- Basado en calidad tecnica general del codigo
- No representa una calificacion academica
- Solo es una estimacion aproximada de calidad tecnica

Archivos proporcionados ({file_count}):

{files_section}

Responde SOLO con JSON valido en este formato exacto, sin texto adicional:

{{
  "summary": "",
  "quality_score": 0,
  "strengths": [],
  "issues": [
    {{
      "severity": "low|medium|high|critical",
      "category": "security|architecture|maintainability|performance|validation|cleanup|readability",
      "file": "ruta/del/archivo.py",
      "description": "",
      "suggestion": ""
    }}
  ],
  "suggestions": [],
  "risk_level": "low|medium|high|critical"
}}
"""

    return prompt


def _as_limited_string(value: object, max_length: int) -> str:
    if not isinstance(value, str):
        return ""

    return value.strip()[:max_length]


def _normalize_string_list(value: object, max_items: int, max_length: int) -> list[str]:
    if not isinstance(value, list):
        return []

    normalized = []
    for item in value[:max_items]:
        text = _as_limited_string(item, max_length)
        if text:
            normalized.append(text)

    return normalized


def _normalize_quality_score(value: object) -> int:
    if isinstance(value, bool):
        return 0

    if isinstance(value, (int, float)):
        return max(0, min(100, int(value)))

    return 0


def _normalize_risk_level(value: object) -> str:
    if isinstance(value, str) and value in VALID_RISK_LEVELS:
        return value

    return "medium"


def _normalize_issue(issue: object) -> dict:
    if not isinstance(issue, dict):
        issue = {}

    severity = issue.get("severity")
    category = issue.get("category")

    if severity not in VALID_SEVERITIES:
        severity = "medium"

    if category not in VALID_CATEGORIES:
        category = "maintainability"

    file_path = _as_limited_string(issue.get("file"), 180) or "multiple"

    return {
        "severity": severity,
        "category": category,
        "file": file_path,
        "description": _as_limited_string(issue.get("description"), 300),
        "suggestion": _as_limited_string(issue.get("suggestion"), 220),
    }


def _normalize_issues(value: object) -> list[dict]:
    if not isinstance(value, list):
        return []

    return [_normalize_issue(issue) for issue in value[:3]]


def generate_ai_feedback(repo_path: str) -> dict:
    if not GEMINI_API_KEY:
        return {
            "enabled": False,
            "provider": "gemini",
            "message": "Retroalimentacion IA no configurada",
            "files_count": 0,
        }

    context = collect_repo_code_context(repo_path)

    if not context.get("files"):
        return {
            "enabled": True,
            "provider": "gemini",
            "summary": "No se encontraron archivos de codigo para analizar",
            "quality_score": 0,
            "strengths": [],
            "issues": [],
            "suggestions": [],
            "risk_level": "low",
            "files_count": 0,
        }

    prompt = build_feedback_prompt(context)

    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
                json={
                    "contents": [
                        {
                            "parts": [
                                {
                                    "text": prompt
                                }
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.2,
                        "maxOutputTokens": 4096,
                        "responseMimeType": "application/json",
                    },
                },
            )

        if response.status_code != 200:
            return {
                "enabled": True,
                "provider": "gemini",
                "summary": "No se pudo generar retroalimentacion IA",
                "quality_score": 0,
                "strengths": [],
                "issues": [],
                "suggestions": [],
                "risk_level": "medium",
                "error": f"HTTP {response.status_code}",
                "files_count": len(context.get("files", [])),
            }

        result = response.json()
        text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")

        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        parsed = json.loads(text)
        if not isinstance(parsed, dict):
            parsed = {}

        normalized_feedback = {
            "summary": _as_limited_string(parsed.get("summary"), 500),
            "quality_score": _normalize_quality_score(parsed.get("quality_score")),
            "strengths": _normalize_string_list(parsed.get("strengths"), 3, 180),
            "issues": _normalize_issues(parsed.get("issues")),
            "suggestions": _normalize_string_list(parsed.get("suggestions"), 2, 220),
            "risk_level": _normalize_risk_level(parsed.get("risk_level")),
        }

        return {
            "enabled": True,
            "provider": "gemini",
            **normalized_feedback,
            "files_count": len(context.get("files", [])),
        }

    except json.JSONDecodeError:
        return {
            "enabled": True,
            "provider": "gemini",
            "summary": "No se pudo interpretar la respuesta de IA",
            "quality_score": 0,
            "strengths": [],
            "issues": [],
            "suggestions": [],
            "risk_level": "medium",
            "raw_response": text if 'text' in dir() else None,
            "files_count": len(context.get("files", [])) if 'context' in dir() else 0,
        }

    except Exception as exc:
        return {
            "enabled": True,
            "provider": "gemini",
            "summary": "No se pudo generar retroalimentacion IA",
            "quality_score": 0,
            "strengths": [],
            "issues": [],
            "suggestions": [],
            "risk_level": "medium",
            "error": str(exc),
            "files_count": len(context.get("files", [])) if 'context' in dir() else 0,
        }
