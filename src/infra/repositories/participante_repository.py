from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from .base_repository import BaseRepository


class ParticipanteRepository(BaseRepository):
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "participantes")

    async def find_by_inscricao(self, nu_inscricao: str) -> Optional[Dict[str, Any]]:
        """Buscar participante por número de inscrição"""
        return await self.collection.find_one({"nu_inscricao": nu_inscricao})

    async def find_by_ano(self, ano: int) -> List[Dict[str, Any]]:
        """Buscar participantes por ano"""
        cursor = self.collection.find({"nu_ano": ano})
        return await cursor.to_list(length=None)

    async def find_by_municipio_prova(
        self, municipio_codigo: int
    ) -> List[Dict[str, Any]]:
        """Buscar participantes por município da prova"""
        cursor = self.collection.find({"municipio_prova_codigo": municipio_codigo})
        return await cursor.to_list(length=None)

    async def get_estatisticas_por_sexo(self) -> List[Dict[str, Any]]:
        """Obter estatísticas por sexo"""
        pipeline = [
            {
                "$group": {
                    "_id": "$sexo",
                    "total": {"$sum": 1},
                    "treineiros": {"$sum": {"$cond": ["$treineiro", 1, 0]}},
                }
            }
        ]
        return await self.aggregate(pipeline)

    async def get_estatisticas_por_faixa_etaria(self) -> List[Dict[str, Any]]:
        """Obter estatísticas por faixa etária"""
        pipeline = [
            {
                "$group": {
                    "_id": "$faixa_etaria",
                    "total": {"$sum": 1},
                    "treineiros": {"$sum": {"$cond": ["$treineiro", 1, 0]}},
                }
            },
            {"$sort": {"_id": 1}},
        ]
        return await self.aggregate(pipeline)

    async def get_estatisticas_por_cor_raca(self) -> List[Dict[str, Any]]:
        """Obter estatísticas por cor/raça"""
        pipeline = [
            {"$group": {"_id": "$cor_raca", "total": {"$sum": 1}}},
            {"$sort": {"total": -1}},
        ]
        return await self.aggregate(pipeline)
