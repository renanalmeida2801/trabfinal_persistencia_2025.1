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

    async def get_estatisticas_por_dependencia(
        self, uf_sigla: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Obter estatísticas por dependência administrativa"""
        match_stage = {}

        if uf_sigla:
            match_stage["uf_sigla"] = uf_sigla.upper()

        pipeline = []

        if match_stage:
            pipeline.append({"$match": match_stage})

        pipeline.extend(
            [
                {
                    "$group": {
                        "_id": "$dependencia_administrativa",
                        "total_escolas": {"$sum": 1},
                        "total_participantes": {"$sum": "$total_participantes"},
                        "media_participantes": {"$avg": "$total_participantes"},
                    }
                },
                {"$sort": {"total_escolas": -1}},
            ]
        )

        return await self.aggregate(pipeline)

    async def get_top_escolas_participantes(
        self, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Obter escolas com mais participantes"""
        cursor = (
            self.collection.find({"total_participantes": {"$gt": 0}})
            .sort("total_participantes", -1)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def get_ranking_por_desempenho(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Obter ranking das escolas por desempenho médio dos participantes"""
        pipeline = [
            {
                "$lookup": {
                    "from": "resultados",
                    "localField": "codigo",
                    "foreignField": "escola_codigo",
                    "as": "resultados",
                }
            },
            {"$match": {"resultados": {"$ne": []}}},
            {
                "$addFields": {
                    "media_geral": {
                        "$avg": [
                            {"$avg": "$resultados.nota_cn"},
                            {"$avg": "$resultados.nota_ch"},
                            {"$avg": "$resultados.nota_lc"},
                            {"$avg": "$resultados.nota_mt"},
                            {"$avg": "$resultados.nota_redacao"},
                        ]
                    },
                    "total_participantes_com_nota": {"$size": "$resultados"},
                }
            },
            {
                "$match": {
                    "media_geral": {"$ne": None},
                    "total_participantes_com_nota": {"$gte": 5},
                }
            },
            {
                "$project": {
                    "codigo": 1,
                    "nome": 1,
                    "municipio_codigo": 1,
                    "uf_sigla": 1,
                    "dependencia_administrativa": 1,
                    "situacao_funcionamento": 1,
                    "media_geral": 1,
                    "total_participantes_com_nota": 1,
                }
            },
            {"$sort": {"media_geral": -1}},
            {"$limit": limit},
        ]
        return await self.aggregate(pipeline)

    async def get_escolas_por_uf(self) -> List[Dict[str, Any]]:
        """Obter contagem de escolas por UF"""
        pipeline = [
            {
                "$group": {
                    "_id": "$uf_sigla",
                    "total_escolas": {"$sum": 1},
                    "total_participantes": {"$sum": "$total_participantes"},
                }
            },
            {"$sort": {"total_escolas": -1}},
        ]
        return await self.aggregate(pipeline)

    async def get_escolas_por_localizacao(self) -> List[Dict[str, Any]]:
        """Obter distribuição de escolas por localização"""
        pipeline = [
            {
                "$group": {
                    "_id": "$localizacao",
                    "total": {"$sum": 1},
                    "total_participantes": {"$sum": "$total_participantes"},
                }
            },
            {"$sort": {"total": -1}},
        ]
        return await self.aggregate(pipeline)

    async def get_estatisticas_escola(self, codigo: int) -> Dict[str, Any]:
        """Obter estatísticas específicas de uma escola"""
        pipeline = [
            {"$match": {"codigo": codigo}},
            {
                "$lookup": {
                    "from": "resultados",
                    "localField": "codigo",
                    "foreignField": "escola_codigo",
                    "as": "resultados",
                }
            },
            {
                "$addFields": {
                    "total_resultados": {"$size": "$resultados"},
                    "media_cn": {"$avg": "$resultados.nota_cn"},
                    "media_ch": {"$avg": "$resultados.nota_ch"},
                    "media_lc": {"$avg": "$resultados.nota_lc"},
                    "media_mt": {"$avg": "$resultados.nota_mt"},
                    "media_redacao": {"$avg": "$resultados.nota_redacao"},
                }
            },
            {
                "$project": {
                    "codigo": 1,
                    "nome": 1,
                    "municipio_codigo": 1,
                    "uf_sigla": 1,
                    "dependencia_administrativa": 1,
                    "total_participantes": 1,
                    "total_resultados": 1,
                    "medias": {
                        "ciencias_natureza": "$media_cn",
                        "ciencias_humanas": "$media_ch",
                        "linguagens_codigos": "$media_lc",
                        "matematica": "$media_mt",
                        "redacao": "$media_redacao",
                    },
                }
            },
        ]
        result = await self.aggregate(pipeline)
        return result[0] if result else {}
