# Backend

Backend inicial de EvaluaGit construido con FastAPI.

## Ejecutar localmente

Crear y activar un entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Levantar el servidor:

```bash
uvicorn app.main:app --reload
```

Verificar estado:

```bash
curl http://localhost:8000/health
```
