import traceback
from typing import Any, Dict, List, Optional

from config.logs import logger
from infra.repositories.area_conhecimento_repository import AreaConhecimentoRepository
from infra.repositories.participante_area_repository import ParticipanteAreaRepository
from models.area_conhecimento import AreaConhecimento


class AreaConhecimentoService:
    def __init__(
        self,
        area_repository: AreaConhecimentoRepository,
        participante_area_repository: ParticipanteAreaRepository,
    ):
        """
        Inicializar o service de áreas de conhecimento.

        Args:
            area_repository (AreaConhecimentoRepository): Repository para áreas
            participante_area_repository (ParticipanteAreaRepository): Repository para relacionamentos

        Returns:
            None

        Exceptions:
            None
        """
        self.area_repository = area_repository
        self.participante_area_repository = participante_area_repository

    async def criar_area_conhecimento(
        self, area_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Criar uma nova área de conhecimento.

        Args:
            area_data (Dict[str, Any]): Dados da área a ser criada

        Returns:
            Dict[str, Any]: Dados da área criada

        Exceptions:
            Exception: Erro durante criação da área
        """
        try:
            codigo = area_data.get("codigo", "N/A")
            logger.info(f"Criando área de conhecimento: {codigo}")

            # Verificar se já existe
            existing = await self.area_repository.find_by_codigo(codigo)
            if existing:
                raise Exception(f"Área com código {codigo} já existe")

            created_area = await self.area_repository.create_area(area_data)
            logger.info(f"Área criada com sucesso: {codigo}")
            return created_area

        except Exception as e:
            logger.error(f"Erro ao criar área de conhecimento: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def obter_area_por_id(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Obter área de conhecimento por ID.

        Args:
            id (str): ID da área

        Returns:
            Optional[Dict[str, Any]]: Dados da área encontrada ou None

        Exceptions:
            Exception: Erro durante busca da área
        """
        try:
            logger.info(f"Buscando área por ID: {id}")
            resultado = await self.area_repository.find_by_id(id)

            if resultado:
                logger.info(f"Área encontrada: {resultado.get('codigo', 'N/A')}")
            else:
                logger.warning(f"Área não encontrada para ID: {id}")

            return resultado

        except Exception as e:
            logger.error(f"Erro ao buscar área por ID {id}: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def obter_area_por_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        """
        Obter área de conhecimento por código.

        Args:
            codigo (str): Código da área de conhecimento

        Returns:
            Optional[Dict[str, Any]]: Dados da área encontrada ou None

        Exceptions:
            Exception: Erro durante busca da área
        """
        try:
            logger.info(f"Buscando área por código: {codigo}")
            resultado = await self.area_repository.find_by_codigo(codigo)

            if resultado:
                logger.info(f"Área encontrada: {codigo}")
            else:
                logger.warning(f"Área não encontrada para código: {codigo}")

            return resultado

        except Exception as e:
            logger.error(f"Erro ao buscar área por código {codigo}: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def listar_areas(
        self,
        skip: int = 0,
        limit: int = 100,
        ativas_apenas: bool = True,
        peso_minimo: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Listar áreas de conhecimento com filtros opcionais.

        Args:
            skip (int): Número de registros a pular. Default: 0
            limit (int): Limite de registros retornados. Default: 100
            ativas_apenas (bool): Filtrar apenas áreas ativas. Default: True
            peso_minimo (Optional[float]): Peso mínimo para filtro. Default: None

        Returns:
            Dict[str, Any]: Dados paginados das áreas com metadados

        Exceptions:
            Exception: Erro durante listagem das áreas
        """
        try:
            filtros_str = f"skip={skip}, limit={limit}, ativas_apenas={ativas_apenas}, peso_minimo={peso_minimo}"
            logger.info(f"Listando áreas de conhecimento - {filtros_str}")

            filter_dict = {}
            if ativas_apenas:
                filter_dict["ativa"] = True
            if peso_minimo is not None:
                filter_dict["peso_default"] = {"$gte": peso_minimo}

            areas = await self.area_repository.find_all(
                skip=skip, limit=limit, filter_dict=filter_dict, sort_by="codigo"
            )
            total = await self.area_repository.count(filter_dict)

            logger.info(f"Encontradas {total} áreas, retornando {len(areas)} registros")

            return {
                "items": areas,
                "total": total,
                "skip": skip,
                "current_page": (skip // limit) + 1 if limit > 0 else 1,
                "total_pages": (total + limit - 1) // limit if limit > 0 else 1,
                "limit": limit,
                "has_more": skip + limit < total,
            }

        except Exception as e:
            logger.error(f"Erro ao listar áreas de conhecimento: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def obter_estatisticas_areas(self) -> Dict[str, Any]:
        """
        Obter estatísticas gerais das áreas de conhecimento.

        Args:
            None

        Returns:
            Dict[str, Any]: Estatísticas formatadas

        Exceptions:
            Exception: Erro durante cálculo das estatísticas
        """
        try:
            logger.info("Calculando estatísticas das áreas de conhecimento")

            stats = await self.participante_area_repository.get_media_por_area()

            resultado = {"total_areas": len(stats), "areas": []}

            for stat in stats:
                area_info = await self.area_repository.find_by_codigo(stat["_id"])
                resultado["areas"].append(
                    {
                        "codigo": stat["_id"],
                        "nome": (
                            area_info.get("nome")
                            if area_info
                            else "Área não encontrada"
                        ),
                        "media_nota": round(stat["media_nota"], 2),
                        "total_participantes": stat["total_participantes"],
                        "nota_maxima": stat["nota_maxima"],
                        "nota_minima": stat["nota_minima"],
                        "media_acertos": round(stat.get("media_acertos", 0), 2),
                        "taxa_presenca": round(stat.get("taxa_presenca", 0) * 100, 2),
                    }
                )

            logger.info(f"Estatísticas calculadas para {len(stats)} áreas")
            return resultado

        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas das áreas: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def obter_comparativo_areas(self) -> Dict[str, Any]:
        """
        Obter comparativo entre todas as áreas de conhecimento.

        Args:
            None

        Returns:
            Dict[str, Any]: Comparativo formatado

        Exceptions:
            Exception: Erro durante geração do comparativo
        """
        try:
            logger.info("Gerando comparativo entre áreas de conhecimento")
            comparativo = (
                await self.participante_area_repository.get_comparativo_areas()
            )

            logger.info(
                f"Comparativo gerado com {comparativo.get('total_areas', 0)} áreas"
            )
            return comparativo

        except Exception as e:
            logger.error(f"Erro ao gerar comparativo das áreas: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    # Adicionar outros métodos conforme necessário...
    async def atualizar_area(
        self, area_id: str, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Atualizar dados de uma área de conhecimento."""
        try:
            logger.info(f"Atualizando área: {area_id}")
            resultado = await self.area_repository.update(area_id, update_data)

            if resultado:
                logger.info(f"Área atualizada com sucesso: {area_id}")
            else:
                logger.warning(f"Falha ao atualizar área: {area_id}")

            return resultado

        except Exception as e:
            logger.error(f"Erro ao atualizar área {area_id}: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def deletar_area(self, area_id: str) -> bool:
        """Excluir uma área de conhecimento."""
        try:
            logger.info(f"Excluindo área: {area_id}")
            resultado = await self.area_repository.delete(area_id)

            if resultado:
                logger.info(f"Área excluída com sucesso: {area_id}")
            else:
                logger.warning(f"Falha ao excluir área: {area_id}")

            return resultado

        except Exception as e:
            logger.error(f"Erro ao excluir área {area_id}: {str(e)}")
            logger.error(traceback.format_exc())
            raise
