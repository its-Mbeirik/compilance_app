"""Health check endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Check API health status."""
    return {"status": "healthy", "service": "compliance-verification-system"}


@router.get("/health/ready")
async def readiness_check():
    """Check if service is ready to accept requests."""
    return {
        "status": "ready",
        "components": {
            "api": "ok",
            "vector_db": "pending",
            "llm": "pending",
        },
    }
