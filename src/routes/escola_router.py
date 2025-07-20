from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from config.logs import logger
from infra.repositories.escola_repository import EscolaRepository
from infra.settings.database import get_database
from schemas.escola_schemas import EscolaCreate
from services.escola_service import EscolaService

router = APIRouter(prefix="/escolas", tags=["Escolas"])


async def get_escola_service():
    """Dependency injection para EscolaService"""
    db = await get_database()
    escola_repo = EscolaRepository(db)
    return EscolaService(escola_repo)


@router.post("/", response_model=Dict[str, Any])
async def criar_escola(
    escola: EscolaCreate, service: EscolaService = Depends(get_escola_service)
):
    """Criar uma nova escola"""

    logger.info(f"Criando nova escola: código {escola.codigo} - {escola.nome or 'N/A'}")
    try:
        created_escola = await service.criar_escola(escola.dict())
        logger.info(f"Escola criada com sucesso: {escola.codigo}")
        return created_escola
    except Exception as e:
        logger.error(f"Erro ao criar escola código {escola.codigo}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{escola_id}", response_model=Dict[str, Any])
async def obter_escola(
    escola_id: str, service: EscolaService = Depends(get_escola_service)
):
    """Obter escola por ID"""
    logger.info(f"Buscando escola por ID: {escola_id}")
    escola = await service.obter_escola_por_id(escola_id)
    if not escola:
        logger.warning(f"Escola não encontrada - ID: {escola_id}")
        raise HTTPException(status_code=404, detail="Escola não encontrada")
    logger.info(f"Escola encontrada: {escola.get('nome', 'N/A')}")
    return escola


@router.get("/codigo/{codigo}", response_model=Dict[str, Any])
async def obter_escola_por_codigo(
    codigo: int, service: EscolaService = Depends(get_escola_service)
):
    """Obter escola por código"""
    logger.info(f"Buscando escola por código: {codigo}")
    escola = await service.obter_escola_por_codigo(codigo)
    if not escola:
        logger.warning(f"Escola não encontrada - código: {codigo}")
        raise HTTPException(status_code=404, detail="Escola não encontrada")
    logger.info(f"Escola encontrada: {escola.get('nome', 'N/A')}")
    return escola


@router.get("/", response_model=Dict[str, Any])
async def listar_escolas(
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    uf: Optional[str] = Query(None, description="Filtrar por UF"),
    municipio: Optional[str] = Query(None, description="Filtrar por município"),
    dependencia_administrativa: Optional[str] = Query(
        None, description="Filtrar por dependência administrativa"
    ),
    localizacao: Optional[str] = Query(None, description="Filtrar por localização"),
    situacao_funcionamento: Optional[str] = Query(
        None, description="Filtrar por situação de funcionamento"
    ),
    service: EscolaService = Depends(get_escola_service),
):
    """Listar escolas com filtros e paginação"""
    return await service.listar_escolas(
        skip=skip,
        limit=limit,
        uf=uf,
        municipio=municipio,
        dependencia_administrativa=dependencia_administrativa,
        localizacao=localizacao,
        situacao_funcionamento=situacao_funcionamento,
    )


@router.get("/estatisticas/por-dependencia", response_model=List[Dict[str, Any]])
async def obter_escolas_por_dependencia(
    service: EscolaService = Depends(get_escola_service),
):
    """Obter distribuição de escolas por dependência administrativa"""
    return await service.obter_escolas_por_dependencia()


@router.get("/estatisticas/ranking-desempenho", response_model=List[Dict[str, Any]])
async def obter_ranking_escolas_por_desempenho(
    limit: int = Query(50, ge=1, le=100, description="Número de escolas no ranking"),
    service: EscolaService = Depends(get_escola_service),
):
    """Obter ranking das escolas por desempenho médio dos participantes"""
    return await service.obter_ranking_escolas_por_desempenho(limit)
