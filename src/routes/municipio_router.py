from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from config.logs import logger
from infra.repositories.municipio_repository import MunicipioRepository
from infra.settings.database import get_database
from schemas.municipio_schemas import (
    MunicipioCreate, 
    MunicipioUpdate,
    MunicipioSimples,
    MunicipioPaginadoResponse,
    MunicipioOperationResponse,
    EstatisticasRegiaoResponse
)
from services.municipio_service import MunicipioService

router = APIRouter(prefix="/municipios", tags=["Municípios"])


async def get_municipio_service():
    """Dependency injection para MunicipioService"""
    db = await get_database()
    municipio_repo = MunicipioRepository(db)
    return MunicipioService(municipio_repo)


@router.post("/", response_model=MunicipioSimples)
async def criar_municipio(
    municipio: MunicipioCreate,
    service: MunicipioService = Depends(get_municipio_service),
):
    """Criar um novo município"""
    logger.info(f"Criando novo município: {municipio.nome} - {municipio.uf_sigla}")
    try:
        resultado = await service.criar_municipio(municipio.dict())
        logger.info(f"Município criado com sucesso: {municipio.nome}")
        return resultado
    except Exception as e:
        logger.error(f"Erro ao criar município {municipio.nome}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{municipio_id}", response_model=MunicipioSimples)
async def obter_municipio(
    municipio_id: str, service: MunicipioService = Depends(get_municipio_service)
):
    """Obter município por ID"""
    logger.info(f"Buscando município por ID: {municipio_id}")
    municipio = await service.obter_municipio_por_id(municipio_id)
    if not municipio:
        logger.warning(f"Município não encontrado - ID: {municipio_id}")
        raise HTTPException(status_code=404, detail="Município não encontrado")
    logger.info(f"Município encontrado: {municipio.get('nome', 'N/A')}")
    return municipio


@router.get("/codigo/{codigo}", response_model=MunicipioSimples)
async def obter_municipio_por_codigo(
    codigo: int, service: MunicipioService = Depends(get_municipio_service)
):
    """Obter município por código"""
    logger.info(f"Buscando município por código: {codigo}")
    municipio = await service.obter_municipio_por_codigo(codigo)
    if not municipio:
        logger.warning(f"Município não encontrado - Código: {codigo}")
        raise HTTPException(status_code=404, detail="Município não encontrado")
    logger.info(f"Município encontrado: {municipio.get('nome', 'N/A')}")
    return municipio


@router.get("/", response_model=MunicipioPaginadoResponse)
async def listar_municipios(
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    uf_sigla: Optional[str] = Query(None, description="Filtrar por UF"),
    regiao: Optional[str] = Query(None, description="Filtrar por região"),
    service: MunicipioService = Depends(get_municipio_service),
):
    """Listar municípios com filtros e paginação"""
    filtros = [f"skip={skip}", f"limit={limit}"]
    if uf_sigla:
        filtros.append(f"uf_sigla={uf_sigla}")
    if regiao:
        filtros.append(f"regiao={regiao}")

    logger.info(f"Listando municípios com filtros: {', '.join(filtros)}")
    resultado = await service.listar_municipios(
        skip=skip, limit=limit, uf_sigla=uf_sigla, regiao=regiao
    )
    logger.info(f"Encontrados {resultado.get('total', 0)} municípios")
    return resultado


@router.put("/{municipio_id}", response_model=MunicipioOperationResponse)
async def atualizar_municipio(
    municipio_id: str,
    municipio_update: MunicipioUpdate,
    service: MunicipioService = Depends(get_municipio_service),
):
    """Atualizar município"""
    # Remove campos None
    update_data = {k: v for k, v in municipio_update.dict().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado para atualizar")

    updated = await service.atualizar_municipio(municipio_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Município não encontrado")

    return {"success": True, "message": "Município atualizado com sucesso", "municipio_id": municipio_id}


@router.delete("/{municipio_id}", response_model=MunicipioOperationResponse)
async def deletar_municipio(
    municipio_id: str, service: MunicipioService = Depends(get_municipio_service)
):
    """Deletar município"""
    deleted = await service.deletar_municipio(municipio_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Município não encontrado")

    return {"success": True, "message": "Município deletado com sucesso", "municipio_id": municipio_id}


@router.get("/estatisticas/regiao", response_model=EstatisticasRegiaoResponse)
async def obter_estatisticas_regiao(
    service: MunicipioService = Depends(get_municipio_service),
):
    """Obter estatísticas agrupadas por região"""
    return await service.obter_estatisticas_por_regiao()
