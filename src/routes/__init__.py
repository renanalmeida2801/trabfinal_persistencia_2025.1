from fastapi import APIRouter
from .municipio_routes import router as municipio_router
from .escola_routes import router as escola_router
from .participante_routes import router as participante_router
from .resultado_routes import router as resultado_router

# Router principal que agrupa todas as rotas
api_router = APIRouter(prefix="/api/v1")

api_router.include_router(municipio_router)
api_router.include_router(escola_router)
api_router.include_router(participante_router)
api_router.include_router(resultado_router)

__all__ = ["api_router"]
