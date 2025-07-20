from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from .base_repository import BaseRepository


class ResultadoRepository(BaseRepository):
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "resultados")

    async def find_by_participante(
        self, participante_inscricao: str
    ) -> Optional[Dict[str, Any]]:
        """Buscar resultado por participante"""
        return await self.collection.find_one(
            {"participante_inscricao": participante_inscricao}
        )

    async def find_by_escola(self, escola_codigo: int) -> List[Dict[str, Any]]:
        """Buscar resultados por escola"""
        cursor = self.collection.find({"escola_codigo": escola_codigo})
        return await cursor.to_list(length=None)

    async def find_by_ano(self, ano: int) -> List[Dict[str, Any]]:
        """Buscar resultados por ano"""
        cursor = self.collection.find({"nu_ano": ano})
        return await cursor.to_list(length=None)

    async def get_media_notas_por_area(self) -> List[Dict[str, Any]]:
        """Obter média das notas por área"""
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "media_cn": {"$avg": "$nota_cn"},
                    "media_ch": {"$avg": "$nota_ch"},
                    "media_lc": {"$avg": "$nota_lc"},
                    "media_mt": {"$avg": "$nota_mt"},
                    "media_redacao": {"$avg": "$nota_redacao"},
                }
            }
        ]
        return await self.aggregate(pipeline)

    async def get_media_por_uf(self) -> List[Dict[str, Any]]:
        """Obter média das notas por UF"""
        pipeline = [
            {
                "$group": {
                    "_id": "$uf_prova_sigla",
                    "media_cn": {"$avg": "$nota_cn"},
                    "media_ch": {"$avg": "$nota_ch"},
                    "media_lc": {"$avg": "$nota_lc"},
                    "media_mt": {"$avg": "$nota_mt"},
                    "media_redacao": {"$avg": "$nota_redacao"},
                    "total_participantes": {"$sum": 1},
                }
            },
            {"$sort": {"media_redacao": -1}},
        ]
        return await self.aggregate(pipeline)

    async def get_notas_acima_media(
        self, nota_corte: float = 600.0
    ) -> List[Dict[str, Any]]:
        """Buscar participantes com nota acima da média em pelo menos uma área"""
        filter_dict = {
            "$or": [
                {"nota_cn": {"$gte": nota_corte}},
                {"nota_ch": {"$gte": nota_corte}},
                {"nota_lc": {"$gte": nota_corte}},
                {"nota_mt": {"$gte": nota_corte}},
                {"nota_redacao": {"$gte": nota_corte}},
            ]
        }
        cursor = self.collection.find(filter_dict)
        return await cursor.to_list(length=None)

    async def get_distribuicao_notas_redacao(self) -> List[Dict[str, Any]]:
        """Obter distribuição das notas de redação"""
        pipeline = [
            {
                "$bucket": {
                    "groupBy": "$nota_redacao",
                    "boundaries": [0, 200, 400, 600, 800, 1000],
                    "default": "Outros",
                    "output": {
                        "count": {"$sum": 1},
                        "media": {"$avg": "$nota_redacao"},
                    },
                }
            }
        ]
        return await self.aggregate(pipeline)
