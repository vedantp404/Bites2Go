"""FastAPI route definitions."""

from .health import router as health_router
from .food import router as food_router

__all__ = ["health_router", "food_router"]

