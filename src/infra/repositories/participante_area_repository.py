from typing import Optional, Dict, Any, List
from infra.repositories.base_repository import BaseRepository
from utils.json_utils import serialize_mongo_document


class ParticipanteAreaRepository(BaseRepository):
    def __init__(self, database):
        super().__init__(database, "participantes_areas_conhecimento")

    async def find_by_participante(
        self, participante_inscricao: str
    ) -> List[Dict[str, Any]]:
        """Buscar áreas de um participante"""
        try:
            cursor = self.collection.find(
                {"participante_inscricao": participante_inscricao}
            )
            result = await cursor.to_list(length=None)
            return serialize_mongo_document(result)
        except Exception as e:
            print(f"Erro ao buscar áreas do participante: {e}")
            return []

    async def find_by_area(
        self, area_codigo: str, skip: int = 0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Buscar participantes de uma área"""
        try:
            cursor = (
                self.collection.find({"area_codigo": area_codigo})
                .skip(skip)
                .limit(limit)
            )
            result = await cursor.to_list(length=limit)
            return serialize_mongo_document(result)
        except Exception as e:
            print(f"Erro ao buscar participantes da área: {e}")
            return []

    async def count_by_area(self, area_codigo: str) -> int:
        """Contar participantes de uma área"""
        try:
            return await self.collection.count_documents({"area_codigo": area_codigo})
        except Exception as e:
            print(f"Erro ao contar participantes da área: {e}")
            return 0

    async def find_by_participante_and_area(
        self, participante_inscricao: str, area_codigo: str
    ) -> Optional[Dict[str, Any]]:
        """Buscar associação específica"""
        try:
            result = await self.collection.find_one(
                {
                    "participante_inscricao": participante_inscricao,
                    "area_codigo": area_codigo,
                }
            )
            return serialize_mongo_document(result)
        except Exception as e:
            print(f"Erro ao buscar associação: {e}")
            return None

    async def get_media_por_area(self) -> List[Dict[str, Any]]:
        """Obter estatísticas por área"""
        try:
            pipeline = [
                {"$match": {"nota": {"$ne": None, "$exists": True}}},
                {
                    "$group": {
                        "_id": "$area_codigo",
                        "media_nota": {"$avg": "$nota"},
                        "total_participantes": {"$sum": 1},
                        "nota_maxima": {"$max": "$nota"},
                        "nota_minima": {"$min": "$nota"},
                        "media_acertos": {"$avg": "$numero_acertos"},
                        "presentes": {
                            "$sum": {"$cond": [{"$eq": ["$presenca", True]}, 1, 0]}
                        },
                    }
                },
                {
                    "$addFields": {
                        "taxa_presenca": {
                            "$divide": ["$presentes", "$total_participantes"]
                        }
                    }
                },
                {"$sort": {"_id": 1}},
            ]

            cursor = self.collection.aggregate(pipeline)
            result = await cursor.to_list(length=None)
            return serialize_mongo_document(result)
        except Exception as e:
            print(f"Erro ao calcular estatísticas por área: {e}")
            return []

    async def get_ranking_participantes_por_area(
        self, area_codigo: str, ano: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Obter ranking de participantes por área"""
        try:
            match_filter = {"area_codigo": area_codigo, "nota": {"$ne": None}}
            if ano:
                match_filter["ano_prova"] = ano

            pipeline = [
                {"$match": match_filter},
                {"$sort": {"nota": -1}},
                {"$limit": 100},  # Top 100
            ]

            cursor = self.collection.aggregate(pipeline)
            result = await cursor.to_list(length=None)
            return serialize_mongo_document(result)
        except Exception as e:
            print(f"Erro ao gerar ranking: {e}")
            return []

    async def get_participantes_destaque_por_area(
        self, area_codigo: str, nota_minima: float, skip: int = 0, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Obter participantes destaque por área"""
        try:
            pipeline = [
                {"$match": {"area_codigo": area_codigo, "nota": {"$gte": nota_minima}}},
                {"$sort": {"nota": -1}},
                {"$skip": skip},
                {"$limit": limit},
            ]

            cursor = self.collection.aggregate(pipeline)
            result = await cursor.to_list(length=None)
            return serialize_mongo_document(result)
        except Exception as e:
            print(f"Erro ao buscar participantes destaque: {e}")
            return []

    async def count_destaque_por_area(
        self, area_codigo: str, nota_minima: float
    ) -> int:
        """Contar participantes destaque por área"""
        try:
            return await self.collection.count_documents(
                {"area_codigo": area_codigo, "nota": {"$gte": nota_minima}}
            )
        except Exception as e:
            print(f"Erro ao contar participantes destaque: {e}")
            return 0

    async def get_distribuicao_notas_por_area(self, area_codigo: str) -> Dict[str, Any]:
        """Obter distribuição de notas por área"""
        try:
            pipeline = [
                {"$match": {"area_codigo": area_codigo, "nota": {"$ne": None}}},
                {
                    "$bucket": {
                        "groupBy": "$nota",
                        "boundaries": [0, 200, 400, 600, 700, 800, 900, 1000],
                        "default": "Outros",
                        "output": {
                            "total_participantes": {"$sum": 1},
                            "media_faixa": {"$avg": "$nota"},
                        },
                    }
                },
            ]

            cursor = self.collection.aggregate(pipeline)
            result = await cursor.to_list(length=None)
            result = serialize_mongo_document(result)

            # Calcular total para percentuais
            total_geral = sum(faixa["total_participantes"] for faixa in result)

            distribuicao = []
            faixa_nomes = {
                0: "0-200",
                200: "200-400",
                400: "400-600",
                600: "600-700",
                700: "700-800",
                800: "800-900",
                900: "900-1000",
            }

            for faixa in result:
                nome_faixa = faixa_nomes.get(faixa["_id"], str(faixa["_id"]))
                distribuicao.append(
                    {
                        "faixa": nome_faixa,
                        "total_participantes": faixa["total_participantes"],
                        "percentual": (
                            round((faixa["total_participantes"] / total_geral) * 100, 2)
                            if total_geral > 0
                            else 0
                        ),
                        "media_faixa": round(faixa["media_faixa"], 2),
                    }
                )

            # Encontrar faixa mais comum
            faixa_mais_comum = (
                max(distribuicao, key=lambda x: x["total_participantes"])["faixa"]
                if distribuicao
                else "N/A"
            )

            return {
                "area_codigo": area_codigo,
                "total_participantes": total_geral,
                "distribuicao_por_faixas": distribuicao,
                "resumo": {
                    "faixa_mais_comum": faixa_mais_comum,
                    "total_faixas": len(distribuicao),
                },
            }
        except Exception as e:
            print(f"Erro ao calcular distribuição de notas: {e}")
            return {
                "area_codigo": area_codigo,
                "total_participantes": 0,
                "distribuicao_por_faixas": [],
                "resumo": {"faixa_mais_comum": "N/A", "total_faixas": 0},
            }

    async def get_comparativo_areas(self) -> Dict[str, Any]:
        """Obter comparativo entre áreas"""
        try:
            pipeline = [
                {"$match": {"nota": {"$ne": None}}},
                {
                    "$group": {
                        "_id": "$area_codigo",
                        "media_nota": {"$avg": "$nota"},
                        "total_participantes": {"$sum": 1},
                        "nota_maxima": {"$max": "$nota"},
                        "nota_minima": {"$min": "$nota"},
                        "desvio_padrao": {"$stdDevPop": "$nota"},
                        "participantes_destaque": {
                            "$sum": {"$cond": [{"$gte": ["$nota", 700]}, 1, 0]}
                        },
                        "presentes": {
                            "$sum": {"$cond": [{"$eq": ["$presenca", True]}, 1, 0]}
                        },
                    }
                },
                {
                    "$addFields": {
                        "taxa_destaque": {
                            "$multiply": [
                                {
                                    "$divide": [
                                        "$participantes_destaque",
                                        "$total_participantes",
                                    ]
                                },
                                100,
                            ]
                        },
                        "taxa_presenca": {
                            "$multiply": [
                                {"$divide": ["$presentes", "$total_participantes"]},
                                100,
                            ]
                        },
                    }
                },
                {"$sort": {"media_nota": -1}},
            ]

            cursor = self.collection.aggregate(pipeline)
            areas_stats = await cursor.to_list(length=None)
            areas_stats = serialize_mongo_document(areas_stats)

            # Calcular totais gerais
            total_participantes_geral = sum(
                area["total_participantes"] for area in areas_stats
            )
            media_geral = (
                sum(
                    area["media_nota"] * area["total_participantes"]
                    for area in areas_stats
                )
                / total_participantes_geral
                if total_participantes_geral > 0
                else 0
            )

            # Adicionar percentual do total para cada área
            for area in areas_stats:
                area["percentual_total"] = (
                    round(
                        (area["total_participantes"] / total_participantes_geral) * 100,
                        2,
                    )
                    if total_participantes_geral > 0
                    else 0
                )
                area["area_codigo"] = area["_id"]
                area["media_nota"] = round(area["media_nota"], 2)
                area["desvio_padrao"] = round(area["desvio_padrao"], 2)
                area["taxa_destaque"] = round(area["taxa_destaque"], 2)
                area["taxa_presenca"] = round(area["taxa_presenca"], 2)

            # Encontrar área com melhor média
            area_melhor_media = (
                max(areas_stats, key=lambda x: x["media_nota"])["area_codigo"]
                if areas_stats
                else "N/A"
            )

            return {
                "total_areas": len(areas_stats),
                "total_participantes_geral": total_participantes_geral,
                "areas": areas_stats,
                "area_melhor_media": area_melhor_media,
                "media_geral": round(media_geral, 2),
            }
        except Exception as e:
            print(f"Erro ao gerar comparativo de áreas: {e}")
            return {
                "total_areas": 0,
                "total_participantes_geral": 0,
                "areas": [],
                "area_melhor_media": "N/A",
                "media_geral": 0.0,
            }
