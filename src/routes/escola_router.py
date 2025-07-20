from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from config.logs import logger
from infra.repositories.escola_repository import EscolaRepository
from infra.settings.database import get_database
from models.escola import Escola
from schemas.escola_schemas import EscolaCreate

router = APIRouter(prefix="/escolas", tags=["Escolas"])


async def get_escola_repository():
    """Dependency injection para EscolaRepository"""
    db = await get_database()
    return EscolaRepository(db)


@router.post("/", response_model=Dict[str, Any])
async def criar_escola(
    escola: EscolaCreate, repo: EscolaRepository = Depends(get_escola_repository)
):
    """Criar uma nova escola"""

    logger.info(f"Criando nova escola: código {escola.codigo} - {escola.nome or 'N/A'}")
    try:
        escola_obj = Escola(**escola.dict())
        created_escola = await repo.create(escola_obj)
        logger.info(f"Escola criada com sucesso: {escola.codigo}")
        return created_escola.dict()
    except Exception as e:
        logger.error(f"Erro ao criar escola código {escola.codigo}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{escola_id}", response_model=Dict[str, Any])
async def obter_escola(
    escola_id: str, repo: EscolaRepository = Depends(get_escola_repository)
):
    """Obter escola por ID"""
    logger.info(f"Buscando escola por ID: {escola_id}")
    escola = await repo.find_by_id(escola_id)
    if not escola:
        logger.warning(f"Escola não encontrada - ID: {escola_id}")
        raise HTTPException(status_code=404, detail="Escola não encontrada")
    logger.info(f"Escola encontrada: {escola.get('nome', 'N/A')}")
    return escola


@router.get("/codigo/{codigo}", response_model=Dict[str, Any])
async def obter_escola_por_codigo(
    codigo: int, repo: EscolaRepository = Depends(get_escola_repository)
):
    """Obter escola por código"""
    escola = await repo.find_by_codigo(codigo)
    if not escola:
        raise HTTPException(status_code=404, detail="Escola não encontrada")
    return escola


@router.get("/", response_model=Dict[str, Any])
async def listar_escolas(
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    municipio_codigo: Optional[int] = Query(
        None, description="Filtrar por código do município"
    ),
    uf_sigla: Optional[str] = Query(None, description="Filtrar por UF"),
    dependencia_administrativa: Optional[int] = Query(
        None, description="Filtrar por dependência administrativa"
    ),
    repo: EscolaRepository = Depends(get_escola_repository),
):
    """Listar escolas com filtros e paginação"""
    filter_dict = {}
    if municipio_codigo:
        filter_dict["municipio_codigo"] = municipio_codigo
    if uf_sigla:
        filter_dict["uf_sigla"] = uf_sigla
    if dependencia_administrativa:
        filter_dict["dependencia_administrativa"] = dependencia_administrativa

    escolas = await repo.find_all(
        skip=skip, limit=limit, filter_dict=filter_dict, sort_by="codigo"
    )
    total = await repo.count(filter_dict)

    return {
        "items": escolas,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": skip + limit < total,
    }


@router.get("/estatisticas/dependencia", response_model=List[Dict[str, Any]])
async def obter_estatisticas_dependencia(
    repo: EscolaRepository = Depends(get_escola_repository),
):
    """Obter estatísticas por dependência administrativa"""
    return await repo.get_estatisticas_por_dependencia()


@router.get("/estatisticas/top-participantes", response_model=List[Dict[str, Any]])
async def obter_top_escolas_participantes(
    limit: int = Query(10, ge=1, le=50, description="Número de escolas no ranking"),
    repo: EscolaRepository = Depends(get_escola_repository),
):
    """Obter ranking das escolas com mais participantes"""
    return await repo.get_top_escolas_participantes(limit)
