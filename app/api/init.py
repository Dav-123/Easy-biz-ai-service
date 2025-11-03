from .health import router as health_router
from .generation import router as generation_router
from .projects import router as projects_router

__all__ = ['health_router', 'generation_router', 'projects_router']
