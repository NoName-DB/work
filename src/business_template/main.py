from fastapi import FastAPI

from .api.api_v1.api import api_router
from .core.logger import configure_logging
from .core.settings import settings


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description="Business-ready starter API (FastAPI + SQLAlchemy)",
    )

    app.include_router(api_router, prefix="/api/v1")

    @app.get("/")
    def root() -> dict[str, str]:
        return {"message": "Business Template API", "docs": "/docs", "health": "/health"}

    @app.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
