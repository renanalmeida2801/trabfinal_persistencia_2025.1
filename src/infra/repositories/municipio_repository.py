from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from config.logs import logger

from .base_repository import BaseRepository


class MunicipioRepository(BaseRepository):
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "municipios")

    async def find_by_codigo(self, codigo: int) -> Optional[Dict[str, Any]]:
        """Buscar município por código"""
        logger.info(f"Repository: Buscando município por código {codigo}")
        resultado = await self.collection.find_one({"codigo": codigo})
        if resultado:
            logger.info(f"Repository: Município encontrado - código {codigo}")
        return resultado

    async def find_by_uf(self, uf_sigla: str) -> List[Dict[str, Any]]:
        """Buscar municípios por UF"""
        cursor = self.collection.find({"uf_sigla": uf_sigla})
        return await cursor.to_list(length=None)

    async def find_by_regiao(self, regiao: str) -> List[Dict[str, Any]]:
        """Buscar municípios por região"""
        cursor = self.collection.find({"regiao": regiao})
        return await cursor.to_list(length=None)

    async def get_estatisticas_por_regiao(self) -> List[Dict[str, Any]]:
        """Obter estatísticas agrupadas por região"""
        pipeline = [
            {
                "$group": {
                    "_id": "$regiao",
                    "total_municipios": {"$sum": 1},
                    "populacao_total": {"$sum": "$populacao"},
                    "pib_medio": {"$avg": "$pib_per_capita"},
                    "idh_medio": {"$avg": "$idh"},
                }
            },
            {"$sort": {"total_municipios": -1}},
        ]
        return await self.aggregate(pipeline)
