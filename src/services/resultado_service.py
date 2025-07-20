from datetime import datetime
from typing import Any, Dict, List, Optional

from infra.repositories.resultado_repository import ResultadoRepository
from models.resultado import Resultado


class ResultadoService:
    def __init__(self, resultado_repository: ResultadoRepository):
        self.resultado_repository = resultado_repository

    async def criar_resultado(self, resultado_data: Dict[str, Any]) -> Dict[str, Any]:
        """Criar um novo resultado"""
        # Calcular campos derivados
        if all(
            key in resultado_data and resultado_data[key] is not None
            for key in ["nota_cn", "nota_ch", "nota_lc", "nota_mt"]
        ):
            resultado_data["media_provas_objetivas"] = (
                resultado_data["nota_cn"]
                + resultado_data["nota_ch"]
                + resultado_data["nota_lc"]
                + resultado_data["nota_mt"]
            ) / 4

        resultado = Resultado(**resultado_data)
        created_resultado = await self.resultado_repository.create(resultado)
        return created_resultado.dict()

    async def obter_resultado_por_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Obter resultado por ID"""
        return await self.resultado_repository.find_by_id(id)

    async def obter_resultado_por_participante(
        self, participante_inscricao: str
    ) -> Optional[Dict[str, Any]]:
        """Obter resultado por participante"""
        return await self.resultado_repository.find_by_participante(
            participante_inscricao
        )

    async def listar_resultados(
        self,
        skip: int = 0,
        limit: int = 100,
        ano: Optional[int] = None,
        escola_codigo: Optional[int] = None,
        uf_prova_sigla: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Listar resultados com filtros opcionais"""
        filter_dict = {}
        if ano:
            filter_dict["nu_ano"] = ano
        if escola_codigo:
            filter_dict["escola_codigo"] = escola_codigo
        if uf_prova_sigla:
            filter_dict["uf_prova_sigla"] = uf_prova_sigla

        resultados = await self.resultado_repository.find_all(
            skip=skip, limit=limit, filter_dict=filter_dict, sort_by="nu_sequencial"
        )
        total = await self.resultado_repository.count(filter_dict)

        return {
            "items": resultados,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total,
        }

    async def obter_media_notas_gerais(self) -> Dict[str, Any]:
        """Obter média geral das notas"""
        medias = await self.resultado_repository.get_media_notas_por_area()
        return medias[0] if medias else {}

    async def obter_ranking_uf(self) -> List[Dict[str, Any]]:
        """Obter ranking das UFs por média das notas"""
        return await self.resultado_repository.get_media_por_uf()

    async def obter_participantes_destaque(
        self, nota_corte: float = 700.0
    ) -> List[Dict[str, Any]]:
        """Obter participantes com notas de destaque"""
        return await self.resultado_repository.get_notas_acima_media(nota_corte)

    async def obter_distribuicao_redacao(self) -> List[Dict[str, Any]]:
        """Obter distribuição das notas de redação"""
        return await self.resultado_repository.get_distribuicao_notas_redacao()

    async def obter_estatisticas_por_periodo(
        self,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Obter estatísticas por período"""
        filter_dict = {}
        if data_inicio and data_fim:
            filter_dict["created_at"] = {"$gte": data_inicio, "$lte": data_fim}

        total = await self.resultado_repository.count(filter_dict)
        medias = await self.resultado_repository.get_media_notas_por_area()

        return {
            "total_resultados": total,
            "periodo": {
                "inicio": data_inicio.isoformat() if data_inicio else None,
                "fim": data_fim.isoformat() if data_fim else None,
            },
            "medias": medias[0] if medias else {},
        }
