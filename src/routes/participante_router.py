from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from infra.repositories.participante_repository import ParticipanteRepository
from infra.settings.database import get_database
from schemas.participante_schemas import (
    DistribuicaoIdadeResponse,
    EstatisticasDemograficasResponse,
    ParticipanteCreate,
    ParticipanteOperationResponse,
    ParticipantePaginadoResponse,
    ParticipanteSimples,
    ParticipantesPorUFResponse,
    ParticipanteUpdate,
)
from services.participante_service import ParticipanteService

router = APIRouter(prefix="/participantes", tags=["Participantes"])


async def get_participante_service():
    """Dependency injection para ParticipanteService"""
    db = await get_database()
    participante_repo = ParticipanteRepository(db)
    return ParticipanteService(participante_repo)


@router.get("/{participante_id}", response_model=ParticipanteSimples)
async def obter_participante(
    participante_id: str,
    service: ParticipanteService = Depends(get_participante_service),
):
    """Obter participante por ID"""
    participante = await service.obter_participante_por_id(participante_id)
    if not participante:
        raise HTTPException(status_code=404, detail="Participante não encontrado")
    return participante


@router.get("/inscricao/{nu_inscricao}", response_model=ParticipanteSimples)
async def obter_participante_por_inscricao(
    nu_inscricao: str,
    service: ParticipanteService = Depends(get_participante_service),
):
    """Obter participante por número de inscrição"""
    participante = await service.obter_participante_por_inscricao(nu_inscricao)
    if not participante:
        raise HTTPException(status_code=404, detail="Participante não encontrado")
    return participante


@router.get("/", response_model=ParticipantePaginadoResponse)
async def listar_participantes(
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    ano: Optional[int] = Query(None, description="Filtrar por ano"),
    sexo: Optional[str] = Query(None, description="Filtrar por sexo (M/F)"),
    uf_residencia: Optional[str] = Query(
        None, description="Filtrar por UF de residência"
    ),
    municipio_residencia: Optional[str] = Query(
        None, description="Filtrar por município de residência"
    ),
    escola_codigo: Optional[int] = Query(
        None, description="Filtrar por código da escola"
    ),
    idade_min: Optional[int] = Query(None, description="Idade mínima"),
    idade_max: Optional[int] = Query(None, description="Idade máxima"),
    service: ParticipanteService = Depends(get_participante_service),
):
    """Listar participantes com filtros e paginação"""
    return await service.listar_participantes(
        skip=skip,
        limit=limit,
        ano=ano,
        uf_residencia=uf_residencia,
        municipio_residencia=municipio_residencia,
        escola_codigo=escola_codigo,
        sexo=sexo,
        idade_min=idade_min,
        idade_max=idade_max,
    )


@router.get(
    "/estatisticas/demograficas", response_model=EstatisticasDemograficasResponse
)
async def obter_estatisticas_demograficas(
    service: ParticipanteService = Depends(get_participante_service),
):
    """Obter estatísticas demográficas dos participantes"""
    return await service.obter_estatisticas_demograficas()


@router.get("/estatisticas/por-uf", response_model=ParticipantesPorUFResponse)
async def obter_participantes_por_uf(
    uf_sigla: Optional[str] = Query(
        None, description="Filtrar por UF específica (opcional)"
    ),
    service: ParticipanteService = Depends(get_participante_service),
):
    """Obter contagem de participantes por UF"""
    return await service.obter_participantes_por_uf(uf_sigla)


@router.get(
    "/estatisticas/distribuicao-idade", response_model=DistribuicaoIdadeResponse
)
async def obter_distribuicao_idade(
    service: ParticipanteService = Depends(get_participante_service),
):
    """Obter distribuição de idades dos participantes"""
    return await service.obter_distribuicao_idade()


@router.post("/", response_model=ParticipanteSimples)
async def criar_participante(
    participante: ParticipanteCreate,
    service: ParticipanteService = Depends(get_participante_service),
):
    """Criar um novo participante"""
    try:
        created_participante = await service.criar_participante(participante.dict())
        return created_participante
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{participante_id}", response_model=ParticipanteOperationResponse)
async def atualizar_participante(
    participante_id: str,
    participante_update: ParticipanteUpdate,
    service: ParticipanteService = Depends(get_participante_service),
):
    """Atualizar participante"""
    # Remove campos None
    update_data = {k: v for k, v in participante_update.dict().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado para atualizar")

    updated = await service.atualizar_participante(participante_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Participante não encontrado")

    return {
        "success": True,
        "message": "Participante atualizado com sucesso",
        "participante_id": participante_id,
    }


@router.delete("/{participante_id}", response_model=ParticipanteOperationResponse)
async def deletar_participante(
    participante_id: str,
    service: ParticipanteService = Depends(get_participante_service),
):
    """Deletar participante"""
    deleted = await service.deletar_participante(participante_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Participante não encontrado")

    return {
        "success": True,
        "message": "Participante deletado com sucesso",
        "participante_id": participante_id,
    }
