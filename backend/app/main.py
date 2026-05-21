from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.ai_analysis import router as ai_analysis_router
from app.routes.analysis import router as analysis_router
from app.routes.analysis_runs import router as analysis_runs_router
from app.routes.auth import router as auth_router
from app.routes.projects import router as projects_router
from app.routes.repositories import router as repositories_router
from app.routes.similarity import router as similarity_router

app = FastAPI(title="EvaluaGit API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(projects_router, prefix="/projects", tags=["projects"])
app.include_router(repositories_router, prefix="/repositories", tags=["repositories"])
app.include_router(analysis_router, prefix="/repositories", tags=["analysis"])
app.include_router(ai_analysis_router, prefix="/repositories", tags=["ai-analysis"])
app.include_router(analysis_runs_router, prefix="/analysis-runs", tags=["analysis-runs"])
app.include_router(similarity_router, tags=["similarity"])


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
