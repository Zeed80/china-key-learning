from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, auth, exams, progress, radicals, study, training
from app.core.config import get_settings
from app.db.session import Base, engine
from app.models import all_models  # noqa: F401


def create_app() -> FastAPI:
    settings = get_settings()
    Base.metadata.create_all(bind=engine)

    app = FastAPI(title="China Key Learning API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)
    app.include_router(radicals.router)
    app.include_router(study.router)
    app.include_router(training.router)
    app.include_router(exams.router)
    app.include_router(progress.router)
    app.include_router(admin.router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
