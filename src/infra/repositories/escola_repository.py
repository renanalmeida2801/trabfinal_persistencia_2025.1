from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository


class EscolaRepository(BaseRepository):
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "escolas")
    
    async def find_by_codigo(self, codigo: int) -> Optional[Dict[str, Any]]:
        """Buscar escola por código"""
        return await self.collection.find_one({"codigo": codigo})
    
    async def find_by_municipio(self, municipio_codigo: int) -> List[Dict[str, Any]]:
        """Buscar escolas por município"""
        cursor = self.collection.find({"municipio_codigo": municipio_codigo})
        return await cursor.to_list(length=None)
    
    async def find_by_uf(self, uf_sigla: str) -> List[Dict[str, Any]]:
        """Buscar escolas por UF"""
        cursor = self.collection.find({"uf_sigla": uf_sigla})
        return await cursor.to_list(length=None)
    
    async def get_estatisticas_por_dependencia(self) -> List[Dict[str, Any]]:
        """Obter estatísticas por dependência administrativa"""
        pipeline = [
            {
                "$group": {
                    "_id": "$dependencia_administrativa",
                    "total_escolas": {"$sum": 1},
                    "total_participantes": {"$sum": "$total_participantes"},
                    "media_participantes": {"$avg": "$total_participantes"}
                }
            },
            {"$sort": {"total_escolas": -1}}
        ]
        return await self.aggregate(pipeline)
    
    async def get_top_escolas_participantes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obter escolas com mais participantes"""
        cursor = self.collection.find({"total_participantes": {"$gt": 0}}).sort("total_participantes", -1).limit(limit)
        return await cursor.to_list(length=limit)
