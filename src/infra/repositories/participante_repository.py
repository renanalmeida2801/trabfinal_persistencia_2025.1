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
        sexo_map = {"M": "Masculino", "F": "Feminino"}

        pipeline = [
            {
                "$group": {
                    "_id": "$sexo",
                    "total": {"$sum": 1},
                    "treineiros": {"$sum": {"$cond": ["$treineiro", 1, 0]}},
                    "regulares": {
                        "$sum": {"$cond": [{"$eq": ["$treineiro", False]}, 1, 0]}
                    },
                }
            },
            {"$sort": {"total": -1}},
        ]

        raw_results = await self.aggregate(pipeline)

        # Formatar resultados
        formatted_results = []
        total_geral = sum(item["total"] for item in raw_results)

        for item in raw_results:
            sexo_desc = sexo_map.get(item["_id"], item["_id"] or "Não informado")
            formatted_results.append(
                {
                    "sexo": sexo_desc,
                    "codigo": item["_id"],
                    "total_participantes": item["total"],
                    "participantes_regulares": item["regulares"],
                    "treineiros": item["treineiros"],
                    "percentual_do_total": round(
                        (item["total"] / max(total_geral, 1)) * 100, 2
                    ),
                    "percentual_treineiros": round(
                        (item["treineiros"] / max(item["total"], 1)) * 100, 2
                    ),
                }
            )

        return formatted_results

    async def get_estatisticas_por_faixa_etaria(self) -> List[Dict[str, Any]]:
        """Obter estatísticas por faixa etária"""
        faixa_etaria_map = {
            1: "Menor que 17 anos",
            2: "17 anos",
            3: "18 anos",
            4: "19 anos",
            5: "20 anos",
            6: "21 anos",
            7: "22 anos",
            8: "23 anos",
            9: "24 anos",
            10: "25 anos",
            11: "Entre 26 e 30 anos",
            12: "Entre 31 e 35 anos",
            13: "Entre 36 e 40 anos",
            14: "Entre 41 e 45 anos",
            15: "Entre 46 e 50 anos",
            16: "Entre 51 e 55 anos",
            17: "Entre 56 e 60 anos",
            18: "Entre 61 e 65 anos",
            19: "Entre 66 e 70 anos",
            20: "Maior que 70 anos",
        }

        pipeline = [
            {
                "$group": {
                    "_id": "$faixa_etaria",
                    "total": {"$sum": 1},
                    "treineiros": {"$sum": {"$cond": ["$treineiro", 1, 0]}},
                    "regulares": {
                        "$sum": {"$cond": [{"$eq": ["$treineiro", False]}, 1, 0]}
                    },
                }
            },
            {"$sort": {"_id": 1}},  # Ordenar por idade crescente
        ]

        raw_results = await self.aggregate(pipeline)

        # Formatar resultados
        formatted_results = []
        total_geral = sum(item["total"] for item in raw_results)

        for item in raw_results:
            faixa_desc = faixa_etaria_map.get(item["_id"], f"Faixa {item['_id']}")
            formatted_results.append(
                {
                    "faixa_etaria": faixa_desc,
                    "codigo_faixa": item["_id"],
                    "total_participantes": item["total"],
                    "participantes_regulares": item["regulares"],
                    "treineiros": item["treineiros"],
                    "percentual_do_total": round(
                        (item["total"] / max(total_geral, 1)) * 100, 2
                    ),
                    "percentual_treineiros": round(
                        (item["treineiros"] / max(item["total"], 1)) * 100, 2
                    ),
                }
            )

        return formatted_results

    async def get_estatisticas_por_cor_raca(self) -> List[Dict[str, Any]]:
        """Obter estatísticas por cor/raça"""
        cor_raca_map = {
            0: "Não declarado",
            1: "Branca",
            2: "Preta",
            3: "Parda",
            4: "Amarela",
            5: "Indígena",
        }

        pipeline = [
            {
                "$group": {
                    "_id": "$cor_raca",
                    "total": {"$sum": 1},
                    "treineiros": {"$sum": {"$cond": ["$treineiro", 1, 0]}},
                    "regulares": {
                        "$sum": {"$cond": [{"$eq": ["$treineiro", False]}, 1, 0]}
                    },
                }
            },
            {"$sort": {"total": -1}},
        ]

        raw_results = await self.aggregate(pipeline)

        # Formatar resultados
        formatted_results = []
        total_geral = sum(item["total"] for item in raw_results)

        for item in raw_results:
            cor_desc = cor_raca_map.get(item["_id"], f"Código {item['_id']}")
            formatted_results.append(
                {
                    "cor_raca": cor_desc,
                    "codigo": item["_id"],
                    "total_participantes": item["total"],
                    "participantes_regulares": item["regulares"],
                    "treineiros": item["treineiros"],
                    "percentual_do_total": round(
                        (item["total"] / max(total_geral, 1)) * 100, 2
                    ),
                    "percentual_treineiros": round(
                        (item["treineiros"] / max(item["total"], 1)) * 100, 2
                    ),
                }
            )

        return formatted_results

    async def get_distribuicao_idade(self) -> List[Dict[str, Any]]:
        """Obter distribuição de idades dos participantes"""
        faixa_etaria_map = {
            1: "Menor que 17 anos",
            2: "17 anos",
            3: "18 anos",
            4: "19 anos",
            5: "20 anos",
            6: "21 anos",
            7: "22 anos",
            8: "23 anos",
            9: "24 anos",
            10: "25 anos",
            11: "Entre 26 e 30 anos",
            12: "Entre 31 e 35 anos",
            13: "Entre 36 e 40 anos",
            14: "Entre 41 e 45 anos",
            15: "Entre 46 e 50 anos",
            16: "Entre 51 e 55 anos",
            17: "Entre 56 e 60 anos",
            18: "Entre 61 e 65 anos",
            19: "Entre 66 e 70 anos",
            20: "Maior que 70 anos",
        }

        pipeline = [
            {
                "$group": {
                    "_id": "$faixa_etaria",
                    "total": {"$sum": 1},
                    "treineiros": {"$sum": {"$cond": ["$treineiro", 1, 0]}},
                    "regulares": {
                        "$sum": {"$cond": [{"$eq": ["$treineiro", False]}, 1, 0]}
                    },
                }
            },
            {
                "$sort": {"total": -1}
            },  # Ordenar por quantidade (mais representativas primeiro)
        ]

        raw_results = await self.aggregate(pipeline)

        # Formatar resultados
        formatted_results = []
        total_geral = sum(item["total"] for item in raw_results)

        for item in raw_results:
            faixa_desc = faixa_etaria_map.get(item["_id"], f"Faixa {item['_id']}")
            formatted_results.append(
                {
                    "faixa_etaria": faixa_desc,
                    "codigo_faixa": item["_id"],
                    "total_participantes": item["total"],
                    "participantes_regulares": item["regulares"],
                    "treineiros": item["treineiros"],
                    "percentual_do_total": round(
                        (item["total"] / max(total_geral, 1)) * 100, 2
                    ),
                    "percentual_treineiros": round(
                        (item["treineiros"] / max(item["total"], 1)) * 100, 2
                    ),
                }
            )

        return formatted_results

    async def get_estatisticas_demograficas(self) -> Dict[str, Any]:
        """Obter estatísticas demográficas completas dos participantes"""
        # Mapeamento de códigos para descrições legíveis
        sexo_map = {"M": "Masculino", "F": "Feminino"}

        cor_raca_map = {
            0: "Não declarado",
            1: "Branca",
            2: "Preta",
            3: "Parda",
            4: "Amarela",
            5: "Indígena",
        }

        faixa_etaria_map = {
            1: "Menor que 17 anos",
            2: "17 anos",
            3: "18 anos",
            4: "19 anos",
            5: "20 anos",
            6: "21 anos",
            7: "22 anos",
            8: "23 anos",
            9: "24 anos",
            10: "25 anos",
            11: "Entre 26 e 30 anos",
            12: "Entre 31 e 35 anos",
            13: "Entre 36 e 40 anos",
            14: "Entre 41 e 45 anos",
            15: "Entre 46 e 50 anos",
            16: "Entre 51 e 55 anos",
            17: "Entre 56 e 60 anos",
            18: "Entre 61 e 65 anos",
            19: "Entre 66 e 70 anos",
            20: "Maior que 70 anos",
        }

        # Agregação para dados brutos
        pipeline = [
            {
                "$facet": {
                    "por_sexo": [
                        {
                            "$group": {
                                "_id": "$sexo",
                                "total": {"$sum": 1},
                                "treineiros": {"$sum": {"$cond": ["$treineiro", 1, 0]}},
                            }
                        }
                    ],
                    "por_faixa_etaria": [
                        {
                            "$group": {
                                "_id": "$faixa_etaria",
                                "total": {"$sum": 1},
                                "treineiros": {"$sum": {"$cond": ["$treineiro", 1, 0]}},
                            }
                        },
                        {"$sort": {"_id": 1}},
                    ],
                    "por_cor_raca": [
                        {"$group": {"_id": "$cor_raca", "total": {"$sum": 1}}},
                        {"$sort": {"total": -1}},
                    ],
                    "por_uf": [
                        {"$match": {"uf_prova": {"$ne": None}}},
                        {"$group": {"_id": "$uf_prova", "total": {"$sum": 1}}},
                        {"$sort": {"total": -1}},
                        {"$limit": 10},  # Top 10 UFs
                    ],
                    "totais": [
                        {
                            "$group": {
                                "_id": None,
                                "total_participantes": {"$sum": 1},
                                "total_treineiros": {
                                    "$sum": {"$cond": ["$treineiro", 1, 0]}
                                },
                                "total_regulares": {
                                    "$sum": {
                                        "$cond": [{"$eq": ["$treineiro", False]}, 1, 0]
                                    }
                                },
                                "idade_media": {
                                    "$avg": {
                                        "$cond": [
                                            {"$ne": ["$idade", None]},
                                            "$idade",
                                            0,
                                        ]
                                    }
                                },
                            }
                        }
                    ],
                }
            }
        ]

        raw_result = await self.aggregate(pipeline)
        if not raw_result:
            return {}

        raw_data = raw_result[0]

        # Formatação dos dados para apresentação mais limpa
        formatted_result = {
            "resumo_geral": {},
            "distribuicao_por_sexo": {},
            "distribuicao_por_idade": [],
            "distribuicao_por_cor_raca": [],
            "top_ufs": [],
        }

        # Resumo geral
        if raw_data.get("totais"):
            totals = raw_data["totais"][0]
            formatted_result["resumo_geral"] = {
                "total_participantes": totals.get("total_participantes", 0),
                "participantes_regulares": totals.get("total_regulares", 0),
                "treineiros": totals.get("total_treineiros", 0),
                "percentual_treineiros": round(
                    (
                        totals.get("total_treineiros", 0)
                        / max(totals.get("total_participantes", 1), 1)
                    )
                    * 100,
                    2,
                ),
                "idade_media": round(totals.get("idade_media", 0), 1)
                if totals.get("idade_media")
                else "Não informado",
            }

        # Distribuição por sexo
        if raw_data.get("por_sexo"):
            total_geral = sum(item["total"] for item in raw_data["por_sexo"])
            for item in raw_data["por_sexo"]:
                sexo_desc = sexo_map.get(item["_id"], item["_id"] or "Não informado")
                formatted_result["distribuicao_por_sexo"][sexo_desc] = {
                    "total": item["total"],
                    "percentual": round((item["total"] / max(total_geral, 1)) * 100, 2),
                    "treineiros": item["treineiros"],
                    "regulares": item["total"] - item["treineiros"],
                }

        if raw_data.get("por_faixa_etaria"):
            faixa_etaria_sorted = sorted(
                raw_data["por_faixa_etaria"], key=lambda x: x["total"], reverse=True
            )[:5]
            for item in faixa_etaria_sorted:
                faixa_desc = faixa_etaria_map.get(item["_id"], f"Faixa {item['_id']}")
                formatted_result["distribuicao_por_idade"].append(
                    {
                        "faixa_etaria": faixa_desc,
                        "total": item["total"],
                        "treineiros": item["treineiros"],
                        "regulares": item["total"] - item["treineiros"],
                    }
                )

        if raw_data.get("por_cor_raca"):
            for item in raw_data["por_cor_raca"][:5]:  # Top 5
                cor_desc = cor_raca_map.get(item["_id"], f"Código {item['_id']}")
                formatted_result["distribuicao_por_cor_raca"].append(
                    {
                        "cor_raca": cor_desc,
                        "total": item["total"],
                        "percentual": round(
                            (
                                item["total"]
                                / max(
                                    formatted_result["resumo_geral"].get(
                                        "total_participantes", 1
                                    ),
                                    1,
                                )
                            )
                            * 100,
                            2,
                        ),
                    }
                )

        if raw_data.get("por_uf"):
            for item in raw_data["por_uf"]:
                formatted_result["top_ufs"].append(
                    {"uf": item["_id"], "total_participantes": item["total"]}
                )

        return formatted_result

    async def get_participantes_por_uf(
        self, uf_sigla: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Obter contagem de participantes por UF"""
        match_stage = {"uf_prova": {"$ne": None}}

        if uf_sigla:
            match_stage["uf_prova"] = uf_sigla.upper()

        pipeline = [
            {"$match": match_stage},
            {
                "$group": {
                    "_id": "$uf_prova",
                    "total": {"$sum": 1},
                    "treineiros": {"$sum": {"$cond": ["$treineiro", 1, 0]}},
                    "regulares": {
                        "$sum": {"$cond": [{"$eq": ["$treineiro", False]}, 1, 0]}
                    },
                }
            },
            {"$sort": {"total": -1}},
        ]

        raw_results = await self.aggregate(pipeline)

        formatted_results = []
        total_geral = sum(item["total"] for item in raw_results)

        for item in raw_results:
            formatted_results.append(
                {
                    "uf": item["_id"],
                    "total_participantes": item["total"],
                    "participantes_regulares": item["regulares"],
                    "treineiros": item["treineiros"],
                    "percentual_do_total": round(
                        (item["total"] / max(total_geral, 1)) * 100, 2
                    ),
                    "percentual_treineiros": round(
                        (item["treineiros"] / max(item["total"], 1)) * 100, 2
                    ),
                }
            )

        return formatted_results
