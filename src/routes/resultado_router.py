from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from infra.repositories.resultado_repository import ResultadoRepository
from infra.settings.database import get_database
from schemas.resultado_schemas import (
    DistribuicaoRedacaoResponse,
    EstatisticasPeriodoResponse,
    MediasGeraisResponse,
    ParticipantesDestaqueResponse,
    RankingUFResponse,
    ResultadoCreate,
    ResultadoOperationResponse,
    ResultadoPaginadoResponse,
    ResultadoSimples,
    ResultadoUpdate,
)
from services.resultado_service import ResultadoService

router = APIRouter(prefix="/resultados", tags=["Resultados"])


async def get_resultado_service():
    """Dependency injection para ResultadoService"""
    db = await get_database()
    resultado_repo = ResultadoRepository(db)
    return ResultadoService(resultado_repo)


@router.post("/", response_model=ResultadoSimples)
async def criar_resultado(
    resultado: ResultadoCreate,
    service: ResultadoService = Depends(get_resultado_service),
):
    """Criar um novo resultado"""
    try:
        return await service.criar_resultado(resultado.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{resultado_id}", response_model=ResultadoSimples)
async def obter_resultado(
    resultado_id: str, service: ResultadoService = Depends(get_resultado_service)
):
    """Obter resultado por ID"""
    resultado = await service.obter_resultado_por_id(resultado_id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Resultado não encontrado")
    return resultado


@router.get("/participante/{participante_inscricao}", response_model=ResultadoSimples)
async def obter_resultado_por_participante(
    participante_inscricao: str,
    service: ResultadoService = Depends(get_resultado_service),
):
    """Obter resultado por participante"""
    resultado = await service.obter_resultado_por_participante(participante_inscricao)
    if not resultado:
        raise HTTPException(status_code=404, detail="Resultado não encontrado")
    return resultado


@router.get("/", response_model=ResultadoPaginadoResponse)
async def listar_resultados(
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    ano: Optional[int] = Query(None, description="Filtrar por ano"),
    escola_codigo: Optional[int] = Query(
        None, description="Filtrar por código da escola"
    ),
    uf_prova_sigla: Optional[str] = Query(None, description="Filtrar por UF da prova"),
    service: ResultadoService = Depends(get_resultado_service),
):
    """Listar resultados com filtros e paginação"""
    return await service.listar_resultados(
        skip=skip,
        limit=limit,
        ano=ano,
        escola_codigo=escola_codigo,
        uf_prova_sigla=uf_prova_sigla,
    )


@router.get("/estatisticas/medias-gerais", response_model=MediasGeraisResponse)
async def obter_medias_gerais(
    service: ResultadoService = Depends(get_resultado_service),
):
    """Obter médias gerais das notas do ENEM"""
    return await service.obter_media_notas_gerais()


@router.get("/estatisticas/ranking-uf", response_model=RankingUFResponse)
async def obter_ranking_uf(service: ResultadoService = Depends(get_resultado_service)):
    """Obter ranking das UFs por média das notas"""
    return await service.obter_ranking_uf()


@router.get(
    "/estatisticas/participantes-destaque", response_model=ParticipantesDestaqueResponse
)
async def obter_participantes_destaque(
    nota_corte: float = Query(700.0, ge=0, le=1000, description="Nota de corte"),
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(10, ge=1, le=100, description="Limite de registros por página"),
    service: ResultadoService = Depends(get_resultado_service),
):
    """Obter participantes com notas de destaque"""
    return await service.obter_participantes_destaque(nota_corte, skip, limit)


@router.get(
    "/estatisticas/distribuicao-redacao", response_model=DistribuicaoRedacaoResponse
)
async def obter_distribuicao_redacao(
    service: ResultadoService = Depends(get_resultado_service),
):
    """Obter distribuição das notas de redação por faixas"""
    return await service.obter_distribuicao_redacao()


@router.get("/estatisticas/periodo", response_model=EstatisticasPeriodoResponse)
async def obter_estatisticas_periodo(
    data_inicio: Optional[datetime] = Query(
        None, description="Data de início (ISO format)"
    ),
    data_fim: Optional[datetime] = Query(None, description="Data de fim (ISO format)"),
    service: ResultadoService = Depends(get_resultado_service),
):
    """Obter estatísticas por período de tempo"""
    return await service.obter_estatisticas_por_periodo(data_inicio, data_fim)


@router.put("/{resultado_id}", response_model=ResultadoOperationResponse)
async def atualizar_resultado(
    resultado_id: str,
    resultado_update: ResultadoUpdate,
    service: ResultadoService = Depends(get_resultado_service),
):
    """Atualizar resultado"""
    # Remove campos None
    update_data = {k: v for k, v in resultado_update.dict().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado para atualizar")

    updated = await service.atualizar_resultado(resultado_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Resultado não encontrado")

    return {
        "success": True,
        "message": "Resultado atualizado com sucesso",
        "resultado_id": resultado_id,
    }


@router.delete("/{resultado_id}", response_model=ResultadoOperationResponse)
async def deletar_resultado(
    resultado_id: str, service: ResultadoService = Depends(get_resultado_service)
):
    """Deletar resultado"""
    deleted = await service.deletar_resultado(resultado_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Resultado não encontrado")

    return {
        "success": True,
        "message": "Resultado deletado com sucesso",
        "resultado_id": resultado_id,
    }
