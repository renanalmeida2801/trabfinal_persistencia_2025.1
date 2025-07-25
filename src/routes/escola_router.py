from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from config.logs import logger
from infra.repositories.escola_repository import EscolaRepository
from infra.settings.database import get_database
from schemas.escola_schemas import (
    EscolaCreate,
    EscolaUpdate,
    EscolaOperationResponse,
    EscolaSimples,
    EscolaPaginadaResponse,
    EscolasPorDependenciaResponse,
    RankingEscolasResponse
)
from services.escola_service import EscolaService

router = APIRouter(prefix="/escolas", tags=["Escolas"])


async def get_escola_service():
    """Dependency injection para EscolaService"""
    db = await get_database()
    escola_repo = EscolaRepository(db)
    return EscolaService(escola_repo)


@router.post("/", response_model=EscolaSimples)
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


@router.get("/{escola_id}", response_model=EscolaSimples)
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


@router.get("/codigo/{codigo}", response_model=EscolaSimples)
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


@router.get("/", response_model=EscolaPaginadaResponse)
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


@router.get("/estatisticas/por-dependencia", response_model=EscolasPorDependenciaResponse)
async def obter_escolas_por_dependencia(
    uf_sigla: Optional[str] = Query(
        None, description="Filtrar por UF específica (opcional)"
    ),
    service: EscolaService = Depends(get_escola_service),
):
    """Obter distribuição de escolas por dependência administrativa"""
    return await service.obter_escolas_por_dependencia(uf_sigla)


@router.get("/estatisticas/ranking-desempenho", response_model=RankingEscolasResponse)
async def obter_ranking_escolas_por_desempenho(
    limit: int = Query(50, ge=1, le=100, description="Número de escolas no ranking"),
    service: EscolaService = Depends(get_escola_service),
):
    """Obter ranking das escolas por desempenho médio dos participantes"""
    return await service.obter_ranking_escolas_por_desempenho(limit)


@router.put("/{escola_id}", response_model=EscolaOperationResponse)
async def atualizar_escola(
    escola_id: str,
    escola_update: EscolaUpdate,
    service: EscolaService = Depends(get_escola_service),
):
    """Atualizar escola"""
    logger.info(f"Atualizando escola - ID: {escola_id}")
    
    update_data = {k: v for k, v in escola_update.dict().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado para atualizar")

    try:
        updated = await service.atualizar_escola(escola_id, update_data)
        if not updated:
            logger.warning(f"Escola não encontrada para atualização - ID: {escola_id}")
            raise HTTPException(status_code=404, detail="Escola não encontrada")
        
        logger.info(f"Escola atualizada com sucesso - ID: {escola_id}")
        return {"success": True, "message": "Escola atualizada com sucesso", "escola_id": escola_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar escola {escola_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{escola_id}", response_model=EscolaOperationResponse)
async def deletar_escola(
    escola_id: str, 
    service: EscolaService = Depends(get_escola_service)
):
    """Deletar escola"""
    logger.info(f"Deletando escola - ID: {escola_id}")
    
    try:
        deleted = await service.deletar_escola(escola_id)
        if not deleted:
            logger.warning(f"Escola não encontrada para exclusão - ID: {escola_id}")
            raise HTTPException(status_code=404, detail="Escola não encontrada")
        
        logger.info(f"Escola deletada com sucesso - ID: {escola_id}")
        return {"success": True, "message": "Escola deletada com sucesso", "escola_id": escola_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar escola {escola_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
