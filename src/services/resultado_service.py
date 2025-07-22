import traceback
from datetime import datetime
from typing import Any, Dict, Optional

from config.logs import logger
from infra.repositories.resultado_repository import ResultadoRepository
from models.resultado import Resultado


class ResultadoService:
    def __init__(self, resultado_repository: ResultadoRepository):
        """
        Inicializar o service de resultados.

        Args:
            resultado_repository (ResultadoRepository): Repository para operações de resultado

        Returns:
            None

        Exceptions:
            None
        """
        self.resultado_repository = resultado_repository

    async def criar_resultado(self, resultado_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Criar um novo resultado.

        Args:
            resultado_data (Dict[str, Any]): Dados do resultado a ser criado

        Returns:
            Dict[str, Any]: Dados do resultado criado

        Exceptions:
            Exception: Erro durante criação do resultado
        """
        try:
            logger.info(
                f"Criando novo resultado para participante: {resultado_data.get('nu_inscricao', 'N/A')}"
            )

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
                logger.info(
                    f"Média calculada: {resultado_data['media_provas_objetivas']}"
                )

            resultado = Resultado(**resultado_data)
            created_resultado = await self.resultado_repository.create(resultado)

            logger.info(f"Resultado criado com sucesso: {created_resultado.get('_id')}")
            return created_resultado.dict()

        except Exception as e:
            logger.error(f"Erro ao criar resultado: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def obter_resultado_por_id(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Obter resultado por ID.

        Args:
            id (str): ID do resultado

        Returns:
            Optional[Dict[str, Any]]: Dados do resultado encontrado ou None

        Exceptions:
            Exception: Erro durante busca do resultado
        """
        try:
            logger.info(f"Buscando resultado por ID: {id}")
            resultado = await self.resultado_repository.find_by_id(id)

            if resultado:
                logger.info(
                    f"Resultado encontrado: {resultado.get('nu_inscricao', 'N/A')}"
                )
            else:
                logger.warning(f"Resultado não encontrado para ID: {id}")

            return resultado

        except Exception as e:
            logger.error(f"Erro ao buscar resultado por ID {id}: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def obter_resultado_por_participante(
        self, participante_inscricao: str
    ) -> Optional[Dict[str, Any]]:
        """
        Obter resultado por participante.

        Args:
            participante_inscricao (str): Número de inscrição do participante

        Returns:
            Optional[Dict[str, Any]]: Dados do resultado encontrado ou None

        Exceptions:
            Exception: Erro durante busca do resultado
        """
        try:
            logger.info(
                f"Buscando resultado por participante: {participante_inscricao}"
            )
            resultado = await self.resultado_repository.find_by_participante(
                participante_inscricao
            )

            if resultado:
                logger.info(
                    f"Resultado encontrado para participante: {participante_inscricao}"
                )
            else:
                logger.warning(
                    f"Resultado não encontrado para participante: {participante_inscricao}"
                )

            return resultado

        except Exception as e:
            logger.error(
                f"Erro ao buscar resultado por participante {participante_inscricao}: {str(e)}"
            )
            logger.error(traceback.format_exc())
            raise

    async def listar_resultados(
        self,
        skip: int = 0,
        limit: int = 100,
        ano: Optional[int] = None,
        escola_codigo: Optional[int] = None,
        uf_prova_sigla: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Listar resultados com filtros opcionais.

        Args:
            skip (int): Número de registros a pular. Default: 0
            limit (int): Limite de registros retornados. Default: 100
            ano (Optional[int]): Filtrar por ano. Default: None
            escola_codigo (Optional[int]): Filtrar por código da escola. Default: None
            uf_prova_sigla (Optional[str]): Filtrar por sigla da UF da prova. Default: None

        Returns:
            Dict[str, Any]: Dados paginados dos resultados com metadados

        Exceptions:
            Exception: Erro durante listagem dos resultados
        """
        try:
            logger.info(
                f"Listando resultados - skip: {skip}, limit: {limit}, filtros: ano={ano}, escola_codigo={escola_codigo}, uf_prova_sigla={uf_prova_sigla}"
            )

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

            logger.info(
                f"Encontrados {total} resultados, retornando {len(resultados)} registros"
            )

            return {
                "items": resultados,
                "total": total,
                "skip": skip,
                "limit": limit,
                "has_more": skip + limit < total,
            }

        except Exception as e:
            logger.error(f"Erro ao listar resultados: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def obter_media_notas_gerais(self) -> Dict[str, Any]:
        """
        Obter média geral das notas.

        Args:
            None

        Returns:
            Dict[str, Any]: Médias das notas por área organizadas

        Exceptions:
            Exception: Erro durante cálculo das médias
        """
        try:
            logger.info("Calculando médias gerais das notas")
            medias = await self.resultado_repository.get_media_notas_por_area()

            logger.info("Médias calculadas com sucesso")
            return medias

        except Exception as e:
            logger.error(f"Erro ao calcular médias gerais: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def obter_ranking_uf(self) -> Dict[str, Any]:
        """
        Obter ranking das UFs por média das notas.

        Args:
            None

        Returns:
            Dict[str, Any]: Ranking das UFs formatado

        Exceptions:
            Exception: Erro durante geração do ranking
        """
        try:
            logger.info("Gerando ranking das UFs por média das notas")
            ranking = await self.resultado_repository.get_media_por_uf()

            logger.info(f"Ranking gerado com {ranking.get('total_ufs', 0)} UFs")
            return ranking

        except Exception as e:
            logger.error(f"Erro ao gerar ranking das UFs: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def obter_participantes_destaque(
        self, nota_corte: float = 700.0, skip: int = 0, limit: int = 10
    ) -> Dict[str, Any]:
        """
        Obter participantes com notas de destaque.

        Args:
            nota_corte (float): Nota mínima para considerar destaque. Default: 700.0
            skip (int): Número de registros a pular. Default: 0
            limit (int): Limite de registros retornados. Default: 10

        Returns:
            Dict[str, Any]: Dados paginados dos participantes com metadados

        Exceptions:
            Exception: Erro durante busca dos participantes
        """
        try:
            logger.info(
                f"Buscando participantes com notas acima de {nota_corte} - skip: {skip}, limit: {limit}"
            )

            # Obter participantes com paginação
            participantes = await self.resultado_repository.get_notas_acima_media(
                nota_corte, skip=skip, limit=limit
            )

            # Contar total de participantes que atendem ao critério
            total = await self.resultado_repository.count_notas_acima_media(nota_corte)

            logger.info(
                f"Encontrados {total} participantes em destaque no total, retornando {len(participantes)} registros"
            )

            return {
                "items": participantes,
                "total": total,
                "skip": skip,
                "limit": limit,
                "has_more": skip + limit < total,
                "current_page": (skip // limit) + 1,
                "total_pages": (total + limit - 1) // limit,
                "criterio": f"Nota >= {nota_corte}",
            }

        except Exception as e:
            logger.error(f"Erro ao buscar participantes destaque: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def obter_distribuicao_redacao(self) -> Dict[str, Any]:
        """
        Obter distribuição das notas de redação.

        Args:
            None

        Returns:
            Dict[str, Any]: Distribuição das notas de redação formatada

        Exceptions:
            Exception: Erro durante cálculo da distribuição
        """
        try:
            logger.info("Calculando distribuição das notas de redação")
            distribuicao = (
                await self.resultado_repository.get_distribuicao_notas_redacao()
            )

            logger.info(
                f"Distribuição calculada com {distribuicao.get('resumo_geral', {}).get('total_participantes', 0)} participantes"
            )
            return distribuicao

        except Exception as e:
            logger.error(f"Erro ao calcular distribuição de redação: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def obter_estatisticas_por_periodo(
        self,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Obter estatísticas por período.

        Args:
            data_inicio (Optional[datetime]): Data de início do período. Default: None
            data_fim (Optional[datetime]): Data de fim do período. Default: None

        Returns:
            Dict[str, Any]: Estatísticas do período com total e médias

        Exceptions:
            Exception: Erro durante cálculo das estatísticas
        """
        try:
            periodo_str = f"{data_inicio.isoformat() if data_inicio else 'início'} até {data_fim.isoformat() if data_fim else 'fim'}"
            logger.info(f"Calculando estatísticas por período: {periodo_str}")

            filter_dict = {}
            if data_inicio and data_fim:
                filter_dict["created_at"] = {"$gte": data_inicio, "$lte": data_fim}

            total = await self.resultado_repository.count(filter_dict)
            medias = await self.resultado_repository.get_media_notas_por_area()

            resultado = {
                "total_resultados": total,
                "periodo": {
                    "inicio": data_inicio.isoformat() if data_inicio else None,
                    "fim": data_fim.isoformat() if data_fim else None,
                },
                "estatisticas": medias if medias else {},
            }

            logger.info(f"Estatísticas calculadas: {total} resultados no período")
            return resultado

        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas por período: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def atualizar_resultado(
        self, resultado_id: str, update_data: Dict[str, Any]
    ) -> bool:
        """
        Atualizar um resultado existente.

        Args:
            resultado_id (str): ID do resultado a ser atualizado
            update_data (Dict[str, Any]): Dados para atualização

        Returns:
            bool: True se atualizado com sucesso, False caso contrário

        Exceptions:
            Exception: Quando ocorre erro na atualização
        """
        try:
            logger.info(f"Atualizando resultado: {resultado_id}")
            updated = await self.resultado_repository.update_by_id(
                resultado_id, update_data
            )

            if updated:
                logger.info(f"Resultado atualizado com sucesso: {resultado_id}")
            else:
                logger.warning(
                    f"Resultado não encontrado para atualização: {resultado_id}"
                )

            return updated

        except Exception as e:
            logger.error(f"Erro ao atualizar resultado {resultado_id}: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def deletar_resultado(self, resultado_id: str) -> bool:
        """
        Deletar um resultado.

        Args:
            resultado_id (str): ID do resultado a ser deletado

        Returns:
            bool: True se deletado com sucesso, False caso contrário

        Exceptions:
            Exception: Quando ocorre erro na deleção
        """
        try:
            logger.info(f"Deletando resultado: {resultado_id}")
            deleted = await self.resultado_repository.delete_by_id(resultado_id)

            if deleted:
                logger.info(f"Resultado deletado com sucesso: {resultado_id}")
            else:
                logger.warning(f"Resultado não encontrado para deleção: {resultado_id}")

            return deleted

        except Exception as e:
            logger.error(f"Erro ao deletar resultado {resultado_id}: {str(e)}")
            logger.error(traceback.format_exc())
            raise
