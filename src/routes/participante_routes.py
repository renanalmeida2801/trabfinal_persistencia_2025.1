from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from infra.repositories.participante_repository import ParticipanteRepository
from infra.settings.database import get_database

router = APIRouter(prefix="/participantes", tags=["Participantes"])


async def get_participante_repository():
    """Dependency injection para ParticipanteRepository"""
    db = await get_database()
    return ParticipanteRepository(db)


@router.get("/{participante_id}", response_model=Dict[str, Any])
async def obter_participante(
    participante_id: str,
    repo: ParticipanteRepository = Depends(get_participante_repository),
):
    """Obter participante por ID"""
    participante = await repo.find_by_id(participante_id)
    if not participante:
        raise HTTPException(status_code=404, detail="Participante não encontrado")
    return participante


@router.get("/inscricao/{nu_inscricao}", response_model=Dict[str, Any])
async def obter_participante_por_inscricao(
    nu_inscricao: str,
    repo: ParticipanteRepository = Depends(get_participante_repository),
):
    """Obter participante por número de inscrição"""
    participante = await repo.find_by_inscricao(nu_inscricao)
    if not participante:
        raise HTTPException(status_code=404, detail="Participante não encontrado")
    return participante


@router.get("/", response_model=Dict[str, Any])
async def listar_participantes(
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    ano: Optional[int] = Query(None, description="Filtrar por ano"),
    sexo: Optional[str] = Query(None, description="Filtrar por sexo (M/F)"),
    treineiro: Optional[bool] = Query(None, description="Filtrar por treineiros"),
    uf_prova: Optional[str] = Query(None, description="Filtrar por UF da prova"),
    repo: ParticipanteRepository = Depends(get_participante_repository),
):
    """Listar participantes com filtros e paginação"""
    filter_dict = {}
    if ano:
        filter_dict["nu_ano"] = ano
    if sexo:
        filter_dict["sexo"] = sexo
    if treineiro is not None:
        filter_dict["treineiro"] = treineiro
    if uf_prova:
        filter_dict["uf_prova"] = uf_prova

    participantes = await repo.find_all(
        skip=skip, limit=limit, filter_dict=filter_dict, sort_by="nu_inscricao"
    )
    total = await repo.count(filter_dict)

    return {
        "items": participantes,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": skip + limit < total,
    }


@router.get("/estatisticas/sexo", response_model=List[Dict[str, Any]])
async def obter_estatisticas_sexo(
    repo: ParticipanteRepository = Depends(get_participante_repository),
):
    """Obter estatísticas por sexo"""
    return await repo.get_estatisticas_por_sexo()


@router.get("/estatisticas/faixa-etaria", response_model=List[Dict[str, Any]])
async def obter_estatisticas_faixa_etaria(
    repo: ParticipanteRepository = Depends(get_participante_repository),
):
    """Obter estatísticas por faixa etária"""
    return await repo.get_estatisticas_por_faixa_etaria()


@router.get("/estatisticas/cor-raca", response_model=List[Dict[str, Any]])
async def obter_estatisticas_cor_raca(
    repo: ParticipanteRepository = Depends(get_participante_repository),
):
    """Obter estatísticas por cor/raça"""
    return await repo.get_estatisticas_por_cor_raca()
