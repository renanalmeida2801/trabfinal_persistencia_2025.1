from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config.logs import logger
from infra.settings.database import close_mongo_connection, connect_to_mongo
from routes import (
    admin_router,
    escola_router,
    municipio_router,
    participante_router,
    resultado_router,
    areas_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciar ciclo de vida da aplicação"""
    logger.info("Iniciando aplicação...")
    await connect_to_mongo()

    logger.info("Aplicação iniciada com sucesso!")

    yield

    logger.info("Finalizando aplicação...")
    await close_mongo_connection()
    logger.info("Aplicação finalizada!")


app = FastAPI(
    title="API ENEM - Dados Abertos",
    description="""
    API RESTful para exploração e manipulação de dados do ENEM (Exame Nacional do Ensino Médio).
    
    ## Funcionalidades
    
    * **Municípios**: Operações CRUD e consultas sobre municípios brasileiros
    * **Escolas**: Informações sobre escolas participantes do ENEM
    * **Participantes**: Dados dos participantes do ENEM
    * **Resultados**: Notas e desempenho dos participantes
    * **Estatísticas**: Análises e agregações dos dados
    
    ## Recursos Avançados
    
    * Paginação em todas as listagens
    * Filtros dinâmicos por múltiplos critérios
    * Consultas por intervalo de datas
    * Agregações e cálculos estatísticos
    * Ranking e comparações regionais
    
    """,
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router.router)
app.include_router(municipio_router.router)
app.include_router(escola_router.router)
app.include_router(participante_router.router)
app.include_router(resultado_router.router)
app.include_router(areas_router.router)


@app.get("/", tags=["Root"])
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "API ENEM - Dados Abertos",
        "version": "1.0.0",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Endpoint para verificar saúde da API"""
    return {"status": "healthy", "message": "API funcionando corretamente"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Erro não tratado: {exc}")
    raise HTTPException(status_code=500, detail="Erro interno do servidor")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
