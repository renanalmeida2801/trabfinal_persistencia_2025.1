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

    async def get_media_notas_por_area(self) -> Dict[str, Any]:
        """Obter média das notas por área"""
        # Mapeamento das áreas para nomes mais descritivos
        areas_map = {
            "cn": "Ciências da Natureza",
            "ch": "Ciências Humanas", 
            "lc": "Linguagens e Códigos",
            "mt": "Matemática",
            "redacao": "Redação"
        }
        
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "media_cn": {"$avg": "$nota_cn"},
                    "media_ch": {"$avg": "$nota_ch"},
                    "media_lc": {"$avg": "$nota_lc"},
                    "media_mt": {"$avg": "$nota_mt"},
                    "media_redacao": {"$avg": "$nota_redacao"},
                    "total_resultados": {"$sum": 1},
                    "participantes_cn": {"$sum": {"$cond": [{"$ne": ["$nota_cn", None]}, 1, 0]}},
                    "participantes_ch": {"$sum": {"$cond": [{"$ne": ["$nota_ch", None]}, 1, 0]}},
                    "participantes_lc": {"$sum": {"$cond": [{"$ne": ["$nota_lc", None]}, 1, 0]}},
                    "participantes_mt": {"$sum": {"$cond": [{"$ne": ["$nota_mt", None]}, 1, 0]}},
                    "participantes_redacao": {"$sum": {"$cond": [{"$ne": ["$nota_redacao", None]}, 1, 0]}}
                }
            }
        ]
        
        raw_result = await self.aggregate(pipeline)
        if not raw_result:
            return {}
            
        data = raw_result[0]
        
        formatted_result = {
            "resumo_geral": {
                "total_resultados": data.get("total_resultados", 0),
                "media_geral_enem": round(
                    (
                        (data.get("media_cn", 0) or 0) +
                        (data.get("media_ch", 0) or 0) + 
                        (data.get("media_lc", 0) or 0) +
                        (data.get("media_mt", 0) or 0)
                    ) / 4, 2
                ) if all([data.get("media_cn"), data.get("media_ch"), 
                         data.get("media_lc"), data.get("media_mt")]) else "Não calculável"
            },
            "medias_por_area": []
        }
        
        areas_data = [
            ("cn", data.get("media_cn"), data.get("participantes_cn", 0)),
            ("ch", data.get("media_ch"), data.get("participantes_ch", 0)),
            ("lc", data.get("media_lc"), data.get("participantes_lc", 0)),
            ("mt", data.get("media_mt"), data.get("participantes_mt", 0)),
            ("redacao", data.get("media_redacao"), data.get("participantes_redacao", 0))
        ]
        
        for area_code, media, participantes in areas_data:
            if media is not None:
                formatted_result["medias_por_area"].append({
                    "area": areas_map[area_code],
                    "codigo_area": area_code,
                    "media": round(media, 2),
                    "total_participantes": participantes,
                    "percentual_participacao": round(
                        (participantes / max(data.get("total_resultados", 1), 1)) * 100, 2
                    )
                })
        
        formatted_result["medias_por_area"].sort(key=lambda x: x["media"], reverse=True)
        
        return formatted_result

    async def get_media_por_uf(self) -> Dict[str, Any]:
        """Obter média das notas por UF com formatação melhorada"""
        # Mapeamento das UFs para nomes completos
        ufs_nomes = {
            "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas",
            "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo",
            "GO": "Goiás", "MA": "Maranhão", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul",
            "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PR": "Paraná",
            "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
            "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina",
            "SP": "São Paulo", "SE": "Sergipe", "TO": "Tocantins"
        }
        
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
            }
        ]
        
        raw_results = await self.aggregate(pipeline)
        if not raw_results:
            return {"ranking": [], "total_ufs": 0}
        
        # Formatação dos dados
        formatted_results = []
        for item in raw_results:
            uf_sigla = item["_id"]
            if not uf_sigla:  # Skip registros sem UF
                continue
                
            # Calcular média geral das provas objetivas
            medias_objetivas = [
                item.get("media_cn", 0) or 0,
                item.get("media_ch", 0) or 0,
                item.get("media_lc", 0) or 0,
                item.get("media_mt", 0) or 0
            ]
            media_geral = sum(medias_objetivas) / len(medias_objetivas)
            
            formatted_item = {
                "posicao": 0,  # Será preenchida após ordenação
                "uf": {
                    "sigla": uf_sigla,
                    "nome": ufs_nomes.get(uf_sigla, uf_sigla)
                },
                "total_participantes": item["total_participantes"],
                "media_geral_objetivas": round(media_geral, 2),
                "areas": {
                    "ciencias_natureza": {
                        "nome": "Ciências da Natureza",
                        "media": round(item.get("media_cn", 0) or 0, 2)
                    },
                    "ciencias_humanas": {
                        "nome": "Ciências Humanas",
                        "media": round(item.get("media_ch", 0) or 0, 2)
                    },
                    "linguagens_codigos": {
                        "nome": "Linguagens e Códigos", 
                        "media": round(item.get("media_lc", 0) or 0, 2)
                    },
                    "matematica": {
                        "nome": "Matemática",
                        "media": round(item.get("media_mt", 0) or 0, 2)
                    },
                    "redacao": {
                        "nome": "Redação",
                        "media": round(item.get("media_redacao", 0) or 0, 2)
                    }
                }
            }
            formatted_results.append(formatted_item)
        
        # Ordenar por média de redação (critério principal) e depois por média geral
        formatted_results.sort(
            key=lambda x: (x["areas"]["redacao"]["media"], x["media_geral_objetivas"]), 
            reverse=True
        )
        
        # Adicionar posição no ranking
        for i, item in enumerate(formatted_results, 1):
            item["posicao"] = i
        
        return {
            "ranking": formatted_results,
            "total_ufs": len(formatted_results),
            "criterio_ordenacao": "Média da Redação (principal) + Média Geral das Provas Objetivas",
            "resumo": {
                "melhor_uf": formatted_results[0]["uf"] if formatted_results else None,
                "maior_participacao": max(formatted_results, key=lambda x: x["total_participantes"])["uf"] if formatted_results else None,
                "total_participantes": sum(item["total_participantes"] for item in formatted_results)
            }
        }

    async def get_notas_acima_media(
        self, nota_corte: float = 600.0, skip: int = 0, limit: int = 10
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
        cursor = self.collection.find(filter_dict).skip(skip).limit(limit).sort("nota_redacao", -1)
        return await cursor.to_list(length=None)

    async def count_notas_acima_media(self, nota_corte: float = 600.0) -> int:
        """Contar participantes com nota acima da média em pelo menos uma área"""
        filter_dict = {
            "$or": [
                {"nota_cn": {"$gte": nota_corte}},
                {"nota_ch": {"$gte": nota_corte}},
                {"nota_lc": {"$gte": nota_corte}},
                {"nota_mt": {"$gte": nota_corte}},
                {"nota_redacao": {"$gte": nota_corte}},
            ]
        }
        return await self.collection.count_documents(filter_dict)

    async def get_distribuicao_notas_redacao(self) -> Dict[str, Any]:
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
                        "nota_maxima": {"$max": "$nota_redacao"},
                        "nota_minima": {"$min": "$nota_redacao"}
                    },
                }
            }
        ]
        
        raw_results = await self.aggregate(pipeline)
        
        faixas_map = {
            0: {"nome": "Muito Baixa", "descricao": "0 - 199 pontos", "min": 0, "max": 199},
            200: {"nome": "Baixa", "descricao": "200 - 399 pontos", "min": 200, "max": 399},
            400: {"nome": "Média", "descricao": "400 - 599 pontos", "min": 400, "max": 599},
            600: {"nome": "Boa", "descricao": "600 - 799 pontos", "min": 600, "max": 799},
            800: {"nome": "Excelente", "descricao": "800 - 1000 pontos", "min": 800, "max": 1000},
            "Outros": {"nome": "Inválidas", "descricao": "Notas nulas ou inválidas", "min": None, "max": None}
        }
        
        distribuicao = []
        total_participantes = sum(item.get("count", 0) for item in raw_results)
        
        for item in raw_results:
            faixa_id = item["_id"]
            info_faixa = faixas_map.get(faixa_id, {"nome": "Desconhecida", "descricao": "N/A"})
            
            distribuicao_item = {
                "faixa": {
                    "nome": info_faixa["nome"],
                    "descricao": info_faixa["descricao"],
                    "limite_inferior": info_faixa.get("min"),
                    "limite_superior": info_faixa.get("max"),
                    "intervalo": f"{info_faixa.get('min', 'N/A')} - {info_faixa.get('max', 'N/A')}" if info_faixa.get("min") is not None else "Inválidas"
                },
                "estatisticas": {
                    "total_participantes": item.get("count", 0),
                    "percentual": round((item.get("count", 0) / max(total_participantes, 1)) * 100, 2),
                    "media_faixa": round(item.get("media", 0), 2) if item.get("media") is not None else None,
                    "nota_maxima": item.get("nota_maxima"),
                    "nota_minima": item.get("nota_minima")
                }
            }
            distribuicao.append(distribuicao_item)
        
        # Ordenar por limite inferior (exceto "Outros" que vai pro final)
        distribuicao.sort(key=lambda x: (x["faixa"]["limite_inferior"] is None, x["faixa"]["limite_inferior"] or 0))
        
        return {
            "distribuicao_por_faixas": distribuicao,
            "resumo_geral": {
                "total_participantes": total_participantes,
                "faixa_predominante": max(distribuicao, key=lambda x: x["estatisticas"]["total_participantes"])["faixa"]["nome"] if distribuicao else "N/A",
                "participantes_com_nota_valida": total_participantes - next((item["estatisticas"]["total_participantes"] for item in distribuicao if item["faixa"]["nome"] == "Inválidas"), 0),
                "media_geral_redacao": round(
                    sum(item["estatisticas"]["media_faixa"] * item["estatisticas"]["total_participantes"] 
                        for item in distribuicao if item["estatisticas"]["media_faixa"] is not None) / 
                    max(sum(item["estatisticas"]["total_participantes"] for item in distribuicao if item["estatisticas"]["media_faixa"] is not None), 1), 2
                )
            }
        }
