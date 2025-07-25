from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from infra.repositories.area_conhecimento_repository import AreaConhecimentoRepository
from infra.repositories.participante_area_repository import ParticipanteAreaRepository
from infra.settings.database import get_database
from services.area_conhecimento_service import AreaConhecimentoService
from schemas.area_schemas import (
    AreaConhecimentoCreate,
    AreaConhecimentoUpdate,
    AreaConhecimentoOperationResponse,
    AreaConhecimentoSimples,
)

router = APIRouter(prefix="/areas", tags=["Áreas de Conhecimento"])


async def get_area_service():
    """Dependency injection para AreaConhecimentoService"""
    db = await get_database()
    area_repo = AreaConhecimentoRepository(db)
    participante_area_repo = ParticipanteAreaRepository(db)
    return AreaConhecimentoService(area_repo, participante_area_repo)


@router.get("/{area_id}")
async def obter_area(
    area_id: str,
    service: AreaConhecimentoService = Depends(get_area_service),
):
    """Obter área por ID"""
    try:
        area = await service.obter_area_por_id(area_id)
        if not area:
            raise HTTPException(status_code=404, detail="Área não encontrada")
        return area
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/codigo/{codigo}")
async def obter_area_por_codigo(
    codigo: str,
    service: AreaConhecimentoService = Depends(get_area_service),
):
    """Obter área por código"""
    try:
        area = await service.obter_area_por_codigo(codigo)
        if not area:
            raise HTTPException(status_code=404, detail="Área não encontrada")
        return area
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/")
async def listar_areas(
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    ativas_apenas: bool = Query(True, description="Listar apenas áreas ativas"),
    peso_minimo: Optional[float] = Query(None, description="Peso mínimo para filtro"),
    service: AreaConhecimentoService = Depends(get_area_service),
):
    """Listar áreas de conhecimento com filtros e paginação"""
    try:
        resultado = await service.listar_areas(
            skip=skip,
            limit=limit,
            ativas_apenas=ativas_apenas,
            peso_minimo=peso_minimo,
        )
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/estatisticas/gerais")
async def obter_estatisticas_areas(
    service: AreaConhecimentoService = Depends(get_area_service),
):
    """Obter estatísticas gerais das áreas de conhecimento"""
    try:
        return await service.obter_estatisticas_areas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/estatisticas/comparativo")
async def obter_comparativo_areas(
    service: AreaConhecimentoService = Depends(get_area_service),
):
    """Obter comparativo entre todas as áreas de conhecimento"""
    try:
        return await service.obter_comparativo_areas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/{area_codigo}/participantes")
async def listar_participantes_area(
    area_codigo: str,
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
):
    """Listar participantes de uma área de conhecimento"""
    try:
        db = await get_database()
        participante_area_repo = ParticipanteAreaRepository(db)

        participantes = await participante_area_repo.find_by_area(
            area_codigo, skip, limit
        )
        total = await participante_area_repo.count_by_area(area_codigo)

        return {
            "items": participantes,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total,
            "current_page": (skip // limit) + 1,
            "total_pages": (total + limit - 1) // limit,
            "area_codigo": area_codigo,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/{area_codigo}/ranking")
async def obter_ranking_area(
    area_codigo: str,
    ano: Optional[int] = Query(None, description="Filtrar por ano específico"),
):
    """Obter ranking de participantes por área de conhecimento"""
    try:
        db = await get_database()
        participante_area_repo = ParticipanteAreaRepository(db)
        area_repo = AreaConhecimentoRepository(db)

        ranking = await participante_area_repo.get_ranking_participantes_por_area(
            area_codigo, ano
        )
        area_info = await area_repo.find_by_codigo(area_codigo)

        return {
            "area": {
                "codigo": area_codigo,
                "nome": (
                    area_info.get("nome", "Área não encontrada")
                    if area_info
                    else "Área não encontrada"
                ),
            },
            "ano": ano,
            "total_participantes": len(ranking),
            "ranking": ranking[:50],  # Top 50
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/{area_codigo}/destaque")
async def obter_participantes_destaque_area(
    area_codigo: str,
    nota_minima: float = Query(
        700.0, description="Nota mínima para considerar destaque"
    ),
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(10, ge=1, le=100, description="Limite de registros"),
):
    """Obter participantes destaque em uma área específica"""
    try:
        db = await get_database()
        participante_area_repo = ParticipanteAreaRepository(db)

        participantes = (
            await participante_area_repo.get_participantes_destaque_por_area(
                area_codigo, nota_minima, skip, limit
            )
        )
        total = await participante_area_repo.count_destaque_por_area(
            area_codigo, nota_minima
        )

        return {
            "items": participantes,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total,
            "current_page": (skip // limit) + 1,
            "total_pages": (total + limit - 1) // limit,
            "area_codigo": area_codigo,
            "criterio": f"Nota >= {nota_minima}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/{area_codigo}/distribuicao-notas")
async def obter_distribuicao_notas_area(
    area_codigo: str,
):
    """Obter distribuição de notas por área de conhecimento"""
    try:
        db = await get_database()
        participante_area_repo = ParticipanteAreaRepository(db)
        distribuicao = await participante_area_repo.get_distribuicao_notas_por_area(
            area_codigo
        )
        return distribuicao
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/participante/{participante_inscricao}")
async def obter_areas_participante(
    participante_inscricao: str,
):
    """Obter todas as áreas de conhecimento de um participante"""
    try:
        db = await get_database()
        participante_area_repo = ParticipanteAreaRepository(db)

        areas = await participante_area_repo.find_by_participante(
            participante_inscricao
        )

        if not areas:
            raise HTTPException(
                status_code=404, detail="Nenhuma área encontrada para este participante"
            )

        # Calcular estatísticas
        notas = [area["nota"] for area in areas if area.get("nota") is not None]
        media_geral = sum(notas) / len(notas) if notas else None
        melhor_area = (
            max(areas, key=lambda x: x.get("nota", 0))["area_codigo"] if areas else None
        )
        pior_area = (
            min(areas, key=lambda x: x.get("nota", 9999))["area_codigo"]
            if areas
            else None
        )

        return {
            "participante_inscricao": participante_inscricao,
            "total_areas": len(areas),
            "areas": areas,
            "media_geral": round(media_geral, 2) if media_geral else None,
            "melhor_area": melhor_area,
            "pior_area": pior_area,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.post("/", response_model=AreaConhecimentoSimples)
async def criar_area(
    area: AreaConhecimentoCreate,
    service: AreaConhecimentoService = Depends(get_area_service),
):
    """Criar uma nova área de conhecimento"""
    try:
        created_area = await service.criar_area_conhecimento(area.model_dump())
        return created_area
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{area_id}", response_model=AreaConhecimentoOperationResponse)
async def atualizar_area(
    area_id: str,
    area_update: AreaConhecimentoUpdate,
    service: AreaConhecimentoService = Depends(get_area_service),
):
    """Atualizar área de conhecimento"""
    # Remove campos None
    update_data = {k: v for k, v in area_update.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado para atualizar")

    try:
        updated = await service.atualizar_area(area_id, update_data)
        if not updated:
            raise HTTPException(status_code=404, detail="Área não encontrada")

        return {
            "success": True,
            "message": "Área atualizada com sucesso",
            "area_id": area_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.delete("/{area_id}", response_model=AreaConhecimentoOperationResponse)
async def deletar_area(
    area_id: str,
    service: AreaConhecimentoService = Depends(get_area_service),
):
    """Deletar área de conhecimento"""
    try:
        deleted = await service.deletar_area(area_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Área não encontrada")

        return {
            "success": True,
            "message": "Área deletada com sucesso",
            "area_id": area_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
