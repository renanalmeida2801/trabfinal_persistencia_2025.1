from datetime import datetime
from typing import Any, Dict, List, Optional

from config.logs import logger
from infra.repositories.municipio_repository import MunicipioRepository
from models.municipio import Municipio


class MunicipioService:
    def __init__(self, municipio_repository: MunicipioRepository):
        self.municipio_repository = municipio_repository

    async def criar_municipio(self, municipio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Criar um novo município"""
        logger.info(f"Serviço: Criando município {municipio_data.get('nome', 'N/A')}")
        municipio = Municipio(**municipio_data)
        created_municipio = await self.municipio_repository.create(municipio)
        logger.info(f"Serviço: Município criado com ID {created_municipio.id}")
        return created_municipio.dict()

    async def obter_municipio_por_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Obter município por ID"""
        logger.info(f"Serviço: Buscando município por ID {id}")
        resultado = await self.municipio_repository.find_by_id(id)
        if resultado:
            logger.info(
                f"Serviço: Município encontrado - {resultado.get('nome', 'N/A')}"
            )
        else:
            logger.warning(f"Serviço: Município não encontrado para ID {id}")
        return resultado

    async def obter_municipio_por_codigo(self, codigo: int) -> Optional[Dict[str, Any]]:
        """Obter município por código"""
        return await self.municipio_repository.find_by_codigo(codigo)

    async def listar_municipios(
        self,
        skip: int = 0,
        limit: int = 100,
        uf_sigla: Optional[str] = None,
        regiao: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Listar municípios com filtros opcionais"""
        filter_dict = {}
        if uf_sigla:
            filter_dict["uf_sigla"] = uf_sigla
        if regiao:
            filter_dict["regiao"] = regiao

        municipios = await self.municipio_repository.find_all(
            skip=skip, limit=limit, filter_dict=filter_dict, sort_by="nome"
        )
        total = await self.municipio_repository.count(filter_dict)

        return {
            "items": municipios,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total,
        }

    async def atualizar_municipio(self, id: str, update_data: Dict[str, Any]) -> bool:
        """Atualizar município"""
        update_data["updated_at"] = datetime.now()
        return await self.municipio_repository.update_by_id(id, update_data)

    async def deletar_municipio(self, id: str) -> bool:
        """Deletar município"""
        return await self.municipio_repository.delete_by_id(id)

    async def obter_estatisticas_por_regiao(self) -> List[Dict[str, Any]]:
        """Obter estatísticas agrupadas por região"""
        return await self.municipio_repository.get_estatisticas_por_regiao()
