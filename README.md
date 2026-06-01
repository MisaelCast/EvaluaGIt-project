# Instituto Tecnológico de Ensenada

## Ingeniería en Sistemas Computacionales

### Backend II / Desarrollo Web II

---

**Semestre:** Noveno

**Estudiante:** Misael Castillo Ríos

**Matrícula:** 19760561

**Fecha:** 31 de mayo de 2026

---

# EvaluaGit

EvaluaGit es una plataforma web para la recepción, seguimiento y análisis académico de repositorios Git. Está pensada para profesores que revisan proyectos de programación y necesitan centralizar entregas, validar requerimientos técnicos, revisar actividad Git, obtener retroalimentación asistida por IA y comparar similitudes entre repositorios de alumnos.

El proyecto integra un frontend en Vue 3, un backend en FastAPI, autenticación con Supabase, base de datos PostgreSQL, análisis con Gemini API y comparación de similitud con Dolos mediante Docker.

---

## Tabla de contenido

- [Objetivo del proyecto](#objetivo-del-proyecto)
- [Problema que resuelve](#problema-que-resuelve)
- [Funciones principales](#funciones-principales)
- [Roles del sistema](#roles-del-sistema)
- [Arquitectura general](#arquitectura-general)
- [Stack tecnológico](#stack-tecnológico)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Flujo general de uso](#flujo-general-de-uso)
- [Módulos principales](#módulos-principales)
- [Modelo de datos](#modelo-de-datos)
- [Endpoints principales](#endpoints-principales)
- [Instalación local](#instalación-local)
- [Variables de entorno](#variables-de-entorno)
- [Base de datos y migraciones](#base-de-datos-y-migraciones)
- [Uso de Dolos](#uso-de-dolos)
- [Scripts útiles](#scripts-útiles)
- [Limitaciones actuales](#limitaciones-actuales)
- [Mejoras futuras](#mejoras-futuras)

---

## Objetivo del proyecto

Desarrollar una plataforma web que permita a profesores gestionar proyectos académicos de programación, recibir repositorios Git de alumnos y ejecutar distintos tipos de análisis sobre las entregas.

EvaluaGit busca apoyar al profesor en tres áreas principales:

1. Revisión técnica del repositorio.
2. Retroalimentación sobre calidad del código mediante IA.
3. Comparación de similitud entre entregas usando Dolos.

El sistema no reemplaza el criterio del profesor. Su objetivo es servir como herramienta de apoyo para organizar entregas, detectar problemas técnicos y señalar posibles coincidencias que requieran revisión manual.

---

## Problema que resuelve

En cursos de programación, revisar proyectos manualmente puede ser lento y repetitivo. El profesor normalmente debe:

- Abrir repositorios uno por uno.
- Revisar si existen archivos requeridos.
- Verificar commits y actividad Git.
- Identificar entregas incompletas.
- Revisar calidad del código.
- Comparar similitudes entre trabajos.
- Llevar control de alumnos y entregas.

EvaluaGit centraliza este proceso para que el profesor pueda revisar proyectos de forma más ordenada y con resultados más claros.

---

## Funciones principales

### Para profesores

- Crear proyectos académicos.
- Configurar requerimientos técnicos del proyecto.
- Compartir un código de unión con alumnos.
- Ver entregas recibidas.
- Revisar datos del alumno y su repositorio.
- Ejecutar análisis técnico individual.
- Ejecutar análisis con IA sobre calidad del código.
- Ejecutar análisis de similitud entre entregas.
- Consultar resultados guardados.
- Eliminar proyectos o entregas.

### Para alumnos

- Iniciar sesión.
- Seleccionar rol como alumno.
- Unirse a proyectos mediante código.
- Vincular un repositorio GitHub.
- Consultar sus proyectos y entregas.

---

## Roles del sistema

EvaluaGit maneja roles para separar permisos y vistas.

| Rol          | Descripción                                                              |
| ------------ | ------------------------------------------------------------------------ |
| `UNASSIGNED` | Usuario autenticado que todavía no ha elegido si será profesor o alumno. |
| `PROFESSOR`  | Usuario que crea proyectos y revisa entregas.                            |
| `STUDENT`    | Usuario que se une a proyectos y vincula repositorios.                   |
| `ADMIN`      | Usuario con permisos amplios para administración.                        |

---

## Arquitectura general

```text
Usuario
  │
  ▼
Frontend Vue 3
  │
  ▼
Backend FastAPI
  │
  ├── PostgreSQL / Supabase
  ├── Supabase Auth
  ├── GitHub repositorios
  ├── Gemini API
  └── Dolos mediante Docker
```

### Descripción

- El frontend gestiona las vistas del profesor y alumno.
- El backend expone endpoints para proyectos, repositorios y análisis.
- Supabase se usa para autenticación y conexión con PostgreSQL.
- Los repositorios se clonan temporalmente para analizarlos.
- Gemini genera retroalimentación técnica sobre el código.
- Dolos compara similitud entre entregas de alumnos.

---

## Stack tecnológico

### Frontend

- Vue 3
- Vite
- TypeScript
- Vue Router
- Pinia
- Tailwind CSS
- Supabase JS

### Backend

- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- GitPython
- httpx
- Uvicorn

### Servicios externos

- Supabase Auth
- Supabase PostgreSQL
- Gemini API
- GitHub
- Dolos CLI mediante Docker

---

## Estructura del proyecto

```text
EvaluaGIt-project-main/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── schemas/
│   │   └── services/
│   ├── alembic/
│   ├── alembic.ini
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── lib/
│   │   ├── router/
│   │   ├── services/
│   │   └── views/
│   ├── package.json
│   └── README.md
│
├── docker-compose.yml
└── README.md
```

---

## Flujo general de uso

### Flujo del profesor

1. El profesor inicia sesión.
2. Selecciona el rol de profesor.
3. Crea un proyecto.
4. Configura requerimientos técnicos.
5. Comparte el código de unión con sus alumnos.
6. Revisa las entregas recibidas.
7. Ejecuta análisis técnico, análisis IA o análisis de similitud.
8. Consulta resultados guardados.

### Flujo del alumno

1. El alumno inicia sesión.
2. Selecciona el rol de alumno.
3. Ingresa el código de unión del proyecto.
4. Vincula su repositorio GitHub.
5. El repositorio queda disponible para revisión del profesor.

---

## Módulos principales

## 1. Gestión de usuarios y autenticación

La autenticación se realiza con Supabase. El backend sincroniza o consulta los datos del usuario autenticado y usa roles para permitir o denegar acciones.

Archivos importantes:

```text
backend/app/db/auth.py
backend/app/routes/auth.py
backend/app/models/user.py
frontend/src/services/auth.ts
frontend/src/services/users.ts
frontend/src/views/OnboardingView.vue
```

---

## 2. Gestión de proyectos

Los profesores pueden crear proyectos, editar información general, configurar requerimientos y compartir códigos de unión.

Un proyecto contiene:

- Nombre.
- Descripción.
- Profesor propietario.
- Código de unión.
- Requerimientos técnicos.
- Fecha de creación.
- Fecha de actualización.

Archivos importantes:

```text
backend/app/models/project.py
backend/app/routes/projects.py
backend/app/schemas/project.py
frontend/src/services/projects.ts
frontend/src/views/ProjectsView.vue
frontend/src/views/ProjectSettingsView.vue
```

---

## 3. Unión de alumnos a proyectos

Los alumnos se unen a un proyecto usando el código generado por el profesor. La relación se guarda en la tabla `project_members`.

Archivos importantes:

```text
backend/app/models/project_member.py
backend/app/services/join_code.py
frontend/src/views/StudentDashboardView.vue
```

---

## 4. Entregas y repositorios

Cada alumno puede vincular un repositorio GitHub a un proyecto. El sistema guarda la URL, rama, estado y datos del último análisis.

Estados posibles del repositorio:

| Estado      | Descripción                  |
| ----------- | ---------------------------- |
| `LINKED`    | Repositorio vinculado.       |
| `ANALYZING` | Análisis técnico en proceso. |
| `ANALYZED`  | Análisis técnico completado. |
| `FAILED`    | Fallo en análisis o clonado. |

Archivos importantes:

```text
backend/app/models/repository.py
backend/app/routes/repositories.py
frontend/src/services/repositories.ts
frontend/src/views/DeliveriesView.vue
frontend/src/views/ProjectDetailView.vue
```

---

## 5. Análisis técnico

El análisis técnico clona temporalmente el repositorio y revisa aspectos básicos del proyecto.

Evalúa:

- Lenguaje detectado.
- Framework detectado.
- Dependencias.
- Existencia de README.
- Archivos requeridos.
- Archivos prohibidos.
- Puntaje de estructura.
- Historial de commits.
- Autores.
- Último commit.
- Cumplimiento de commits mínimos.

Archivos importantes:

```text
backend/app/routes/analysis.py
backend/app/routes/analysis_runs.py
backend/app/models/analysis_run.py
backend/app/services/structure_analyzer.py
backend/app/services/git_analyzer.py
frontend/src/services/analysis.ts
frontend/src/views/AnalysisResultView.vue
```

El resultado se guarda en `analysis_runs.result_json`.

---

## 6. Análisis con IA

El análisis con IA usa Gemini API para generar retroalimentación técnica sobre la calidad del código.

Puede detectar:

- Malas prácticas.
- Hardcodeos relevantes.
- Problemas de mantenibilidad.
- Riesgos técnicos.
- Problemas de arquitectura.
- Validaciones faltantes.
- Código aparentemente innecesario.

El análisis es independiente del análisis técnico. Se ejecuta con el endpoint de IA y se guarda en `ai_analysis_runs`.

Archivos importantes:

```text
backend/app/services/ai_feedback_service.py
backend/app/routes/ai_analysis.py
backend/app/models/ai_analysis_run.py
frontend/src/services/aiAnalysis.ts
frontend/src/components/AiAnalysisResult.vue
```

### Estructura general del resultado IA

```json
{
  "summary": "Resumen breve",
  "quality_score": 85,
  "strengths": [],
  "issues": [
    {
      "severity": "medium",
      "category": "maintainability",
      "file": "src/App.vue",
      "description": "Descripción del problema",
      "suggestion": "Sugerencia"
    }
  ],
  "suggestions": [],
  "risk_level": "low",
  "files_count": 41
}
```

---

## 7. Análisis de similitud con Dolos

El análisis de similitud compara entregas de un mismo proyecto usando Dolos. EvaluaGit no afirma plagio; clasifica coincidencias para que el profesor decida si debe revisar manualmente.

Clasificación usada:

| Rango      | Interpretación                     |
| ---------- | ---------------------------------- |
| 0% - 49%   | Coincidencia normal o irrelevante. |
| 50% - 69%  | Revisar solo si hay contexto.      |
| 70% - 84%  | Similitud relevante.               |
| 85% - 100% | Similitud alta o muy sospechosa.   |

Archivos importantes:

```text
backend/app/services/dolos_service.py
backend/app/routes/similarity.py
backend/app/models/similarity_run.py
frontend/src/services/similarity.ts
frontend/src/views/ProjectDetailView.vue
```

El resultado se guarda en `similarity_runs.result_json`.

---

## Modelo de datos

### users

Guarda usuarios sincronizados con Supabase.

Campos principales:

- `id`
- `supabase_id`
- `email`
- `full_name`
- `avatar_url`
- `role`
- `created_at`
- `updated_at`

### projects

Guarda proyectos creados por profesores.

Campos principales:

- `id`
- `professor_id`
- `name`
- `description`
- `requirements`
- `due_date`
- `join_code`
- `created_at`
- `updated_at`

### project_members

Relaciona usuarios con proyectos.

Campos principales:

- `id`
- `project_id`
- `user_id`
- `role`
- `created_at`

### repositories

Guarda entregas de alumnos.

Campos principales:

- `id`
- `project_id`
- `student_id`
- `repo_url`
- `branch`
- `status`
- `last_commit_hash`
- `last_analyzed_at`
- `created_at`
- `updated_at`

### analysis_runs

Guarda ejecuciones del análisis técnico.

### ai_analysis_runs

Guarda ejecuciones del análisis con IA.

### similarity_runs

Guarda ejecuciones del análisis de similitud con Dolos.

---

## Endpoints principales

> Las rutas pueden ajustarse según el entorno. En local el backend normalmente corre en `http://localhost:8000`.

### Salud

```http
GET /health
```

### Autenticación y usuario

```http
GET /auth/me
POST /auth/sync
```

### Proyectos

```http
GET /projects
POST /projects
GET /projects/{project_id}
PATCH /projects/{project_id}
DELETE /projects/{project_id}
POST /projects/join
GET /projects/joined
```

### Repositorios

```http
POST /repositories
GET /repositories/mine
GET /repositories/projects/{project_id}/repositories
GET /repositories/{repo_id}
DELETE /repositories/{repo_id}
```

### Análisis técnico

```http
POST /repositories/{repo_id}/analyze
GET /analysis-runs/{analysis_run_id}
```

### Análisis IA

```http
POST /repositories/{repo_id}/ai-analysis
GET /repositories/{repo_id}/ai-analysis/latest
```

### Similitud

```http
GET /similarity/dolos/status
POST /projects/{project_id}/similarity/analyze
GET /projects/{project_id}/similarity/latest
```

---

## Instalación local

## Requisitos previos

- Python 3.10 o superior.
- Node.js compatible con el frontend.
- PostgreSQL local o Supabase PostgreSQL.
- Docker para usar Dolos.
- Git instalado.
- Cuenta de Supabase.
- API key de Gemini si se usará análisis IA.

---

## 1. Clonar el proyecto

```bash
git clone <URL_DEL_REPOSITORIO>
cd EvaluaGIt-project-main
```

---

## 2. Levantar PostgreSQL local con Docker

El proyecto incluye un `docker-compose.yml` con PostgreSQL local.

```bash
docker compose up -d
```

Por defecto expone PostgreSQL en el puerto local `5433`.

---

## 3. Configurar backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Crear archivo `.env` a partir del ejemplo:

```bash
cp .env.example .env
```

Configurar variables reales en `backend/.env`.

Ejecutar migraciones:

```bash
alembic upgrade head
```

Levantar backend:

```bash
uvicorn app.main:app --reload
```

Verificar:

```bash
curl http://localhost:8000/health
```

---

## 4. Configurar frontend

```bash
cd frontend
npm install
```

Crear archivo `.env` a partir del ejemplo:

```bash
cp .env.example .env
```

Configurar variables reales en `frontend/.env`.

Levantar frontend:

```bash
npm run dev
```

Normalmente estará disponible en:

```text
http://localhost:5173
```

---

## Variables de entorno

### Backend

Archivo: `backend/.env`

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/evaluagit
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu_anon_key
SUPABASE_SERVICE_ROLE_KEY=tu_service_role_key
GEMINI_API_KEY=tu_api_key_de_gemini
```

> No subas `.env` al repositorio.

### Frontend

Archivo: `frontend/.env`

```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://tu-proyecto.supabase.co
VITE_SUPABASE_ANON_KEY=tu_anon_key
```

---

## Base de datos y migraciones

El backend usa Alembic para manejar migraciones.

### Crear migración

```bash
cd backend
alembic revision --autogenerate -m "descripcion del cambio"
```

### Aplicar migraciones

```bash
alembic upgrade head
```

### Ver migración actual

```bash
alembic current
```

### Ver última migración disponible

```bash
alembic heads
```

---

## Uso de Dolos

Dolos se ejecuta mediante Docker. Primero se debe descargar la imagen:

```bash
docker pull ghcr.io/dodona-edu/dolos-cli:latest
```

Verificar estado desde el backend:

```bash
cd backend
python3 -c "from app.services.dolos_service import get_dolos_status; print(get_dolos_status())"
```

Respuesta esperada:

```python
{
  'docker_available': True,
  'image': 'ghcr.io/dodona-edu/dolos-cli:latest',
  'image_available': True,
  'ready': True
}
```

Si `ready` es `False`, el análisis de similitud no podrá ejecutarse correctamente.

---

## Scripts útiles

### Backend

```bash
cd backend
uvicorn app.main:app --reload
python3 -m py_compile app/main.py
alembic upgrade head
```

### Frontend

```bash
cd frontend
npm run dev
npm run type-check
npm run build
```

### Docker PostgreSQL

```bash
docker compose up -d
docker compose down
```

---

## Seguridad y limpieza temporal

EvaluaGit clona repositorios de forma temporal en el servidor para analizarlos. Después del análisis, las carpetas temporales se limpian.

Rutas temporales usadas:

```text
/tmp/repos
/tmp/dolos
```

Medidas implementadas:

- Validación de URL para aceptar solo repositorios de GitHub por HTTPS.
- Validación de rama.
- Exclusión de archivos sensibles en análisis IA y Dolos.
- Limpieza de carpetas temporales después de analizar.
- Separación de permisos por rol.
- Persistencia de resultados en tablas separadas.

---

## Limitaciones actuales

- El análisis técnico es básico y no reemplaza una revisión manual completa.
- El análisis IA depende de Gemini API y de conexión a internet.
- Dolos requiere Docker disponible en el entorno donde corre el backend.
- El análisis de similitud ayuda a detectar coincidencias, pero no confirma plagio.
- La ejecución de análisis puede tardar si los repositorios son grandes.
- La configuración de despliegue todavía puede requerir ajustes de CORS, Dockerfile y entorno productivo.

---

## Mejoras futuras

- Reporte combinado por alumno.
- Exportación a PDF.
- Historial completo de análisis.
- Dashboard con métricas reales.
- Cola de trabajos en segundo plano.
- Notificaciones de análisis completado.
- Configuración avanzada de IA.
- Configuración avanzada de Dolos.
- Soporte para repositorios privados.
- Mejoras de seguridad y manejo de errores global.
- Despliegue productivo con Docker Compose o VPS.

---

## Estado actual del MVP

EvaluaGit ya cuenta con una base funcional para mostrar en una demo académica:

- Gestión de proyectos.
- Unión de alumnos por código.
- Vinculación de repositorios.
- Análisis técnico.
- Análisis IA con Gemini.
- Análisis de similitud con Dolos.
- Persistencia de resultados.
- Vistas para profesor y alumno.

El proyecto está en una etapa MVP funcional. Todavía requiere pulido visual, pruebas completas y ajustes de despliegue antes de considerarse listo para producción.

---
