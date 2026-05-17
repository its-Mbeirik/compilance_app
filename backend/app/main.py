"""FastAPI application factory and configuration."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.api.routes import contracts, compliance, health
from app.core.config import get_settings
from app.models.database import init_db, enable_pgvector

settings = get_settings()

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Database setup
engine = create_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Get database session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    logger.info("Starting Compliance Verification System...")
    try:
        # Initialize database
        logger.info("Initializing database...")
        enable_pgvector(SessionLocal())
        init_db(engine)
        logger.info("✓ Database initialized")

        # Log database stats
        from app.services.vector_store import VectorStore
        db = SessionLocal()
        try:
            vs = VectorStore(db)
            stats = vs.get_database_stats()
            logger.info(f"✓ Legal corpus loaded: {stats['total_documents']} documents")
            for law_code, count in stats['by_law_code'].items():
                logger.info(f"  - {law_code}: {count} articles")
        finally:
            db.close()

    except Exception as e:
        logger.error(f"✗ Initialization failed: {e}")

    yield
    logger.info("Shutting down...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    app = FastAPI(
        title="Compliance Verification System",
        description="Multi-agent system for contract compliance verification",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(contracts.router, prefix="/api/v1", tags=["contracts"])
    app.include_router(compliance.router, prefix="/api/v1", tags=["compliance"])

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
    )
