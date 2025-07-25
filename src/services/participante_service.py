import traceback
from typing import Any, Dict, List, Optional

from config.logs import logger
from infra.repositories.participante_repository import ParticipanteRepository
from models.participante import Participante


class ParticipanteService:
    def __init__(self, participante_repository: ParticipanteRepository):
        """
        Inicializar o service de participantes.

        Args:
            participante_repository (ParticipanteRepository): Repository para operações de participante

        Returns:
            None

        Exceptions:
            None
        """
        self.participante_repository = participante_repository

    async def criar_participante(
        self, participante_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Criar um novo participante.

        Args:
            participante_data (Dict[str, Any]): Dados do participante a ser criado

        Returns:
            Dict[str, Any]: Dados do participante criado

        Exceptions:
            Exception: Erro durante criação do participante
        """
        try:
            nu_inscricao = participante_data.get("nu_inscricao", "N/A")
            logger.info(f"Criando participante: {nu_inscricao}")

            participante = Participante(**participante_data)
            created_participante = await self.participante_repository.create(
                participante
            )

            logger.info(f"Participante criado com sucesso: {nu_inscricao}")
            return created_participante.dict()

        except Exception as e:
            logger.error(f"Erro ao criar participante: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def obter_participante_por_id(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Obter participante por ID.

        Args:
            id (str): ID do participante

        Returns:
            Optional[Dict[str, Any]]: Dados do participante encontrado ou None

        Exceptions:
            Exception: Erro durante busca do participante
        """
        try:
            logger.info(f"Buscando participante por ID: {id}")
            resultado = await self.participante_repository.find_by_id(id)

            if resultado:
                logger.info(
                    f"Participante encontrado: {resultado.get('nu_inscricao', 'N/A')}"
                )
            else:
                logger.warning(f"Participante não encontrado para ID: {id}")

            return resultado

        except Exception as e:
            logger.error(f"Erro ao buscar participante por ID {id}: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def obter_participante_por_inscricao(
        self, nu_inscricao: str
    ) -> Optional[Dict[str, Any]]:
        """
        Obter participante por número de inscrição.

        Args:
            nu_inscricao (str): Número de inscrição do participante

        Returns:
            Optional[Dict[str, Any]]: Dados do participante encontrado ou None

        Exceptions:
            Exception: Erro durante busca do participante
        """
        try:
            logger.info(f"Buscando participante por inscrição: {nu_inscricao}")
            resultado = await self.participante_repository.find_by_inscricao(
                nu_inscricao
            )

            if resultado:
                logger.info(f"Participante encontrado: {nu_inscricao}")
            else:
                logger.warning(
                    f"Participante não encontrado para inscrição: {nu_inscricao}"
                )

            return resultado

        except Exception as e:
            logger.error(
                f"Erro ao buscar participante por inscrição {nu_inscricao}: {str(e)}"
            )
            logger.error(traceback.format_exc())
            raise

    async def listar_participantes(
        self,
        skip: int = 0,
        limit: int = 100,
        ano: Optional[int] = None,
        uf_residencia: Optional[str] = None,
        municipio_residencia: Optional[str] = None,
        escola_codigo: Optional[int] = None,
        sexo: Optional[str] = None,
        idade_min: Optional[int] = None,
        idade_max: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Listar participantes com filtros opcionais.

        Args:
            skip (int): Número de registros a pular. Default: 0
            limit (int): Limite de registros retornados. Default: 100
            ano (Optional[int]): Filtrar por ano. Default: None
            uf_residencia (Optional[str]): Filtrar por UF de residência. Default: None
            municipio_residencia (Optional[str]): Filtrar por município de residência. Default: None
            escola_codigo (Optional[int]): Filtrar por código da escola. Default: None
            sexo (Optional[str]): Filtrar por sexo. Default: None
            idade_min (Optional[int]): Idade mínima. Default: None
            idade_max (Optional[int]): Idade máxima. Default: None

        Returns:
            Dict[str, Any]: Dados paginados dos participantes com metadados

        Exceptions:
            Exception: Erro durante listagem dos participantes
        """
        try:
            filtros_str = f"skip={skip}, limit={limit}, ano={ano}, uf_residencia={uf_residencia}, municipio_residencia={municipio_residencia}, escola_codigo={escola_codigo}, sexo={sexo}, idade_min={idade_min}, idade_max={idade_max}"
            logger.info(f"Listando participantes - {filtros_str}")

            filter_dict = {}
            if ano:
                filter_dict["nu_ano"] = ano
            if uf_residencia:
                filter_dict["uf_residencia"] = uf_residencia
            if municipio_residencia:
                filter_dict["municipio_residencia"] = municipio_residencia
            if escola_codigo:
                filter_dict["escola_codigo"] = escola_codigo
            if sexo:
                filter_dict["tp_sexo"] = sexo
            if idade_min or idade_max:
                idade_filter = {}
                if idade_min:
                    idade_filter["$gte"] = idade_min
                if idade_max:
                    idade_filter["$lte"] = idade_max
                filter_dict["nu_idade"] = idade_filter

            participantes = await self.participante_repository.find_all(
                skip=skip, limit=limit, filter_dict=filter_dict, sort_by="nu_inscricao"
            )
            total = await self.participante_repository.count(filter_dict)

            logger.info(
                f"Encontrados {total} participantes, retornando {len(participantes)} registros"
            )

            return {
                "items": participantes,
                "total": total,
                "skip": skip,
                "current_page": (skip // limit) + 1 if limit > 0 else 1,
                "total_pages": (total + limit - 1) // limit if limit > 0 else 1,
                "limit": limit,
                "has_more": skip + limit < total,
            }

        except Exception as e:
            logger.error(f"Erro ao listar participantes: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def obter_estatisticas_demograficas(self) -> Dict[str, Any]:
        """
        Obter estatísticas demográficas dos participantes.

        Args:
            None

        Returns:
            Dict[str, Any]: Estatísticas demográficas dos participantes

        Exceptions:
            Exception: Erro durante cálculo das estatísticas
        """
        try:
            logger.info("Calculando estatísticas demográficas dos participantes")
            estatisticas = (
                await self.participante_repository.get_estatisticas_demograficas()
            )

            logger.info("Estatísticas demográficas calculadas com sucesso")
            return estatisticas

        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas demográficas: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def obter_participantes_por_uf(
        self, uf_sigla: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obter contagem de participantes por UF.

        Args:
            uf_sigla (Optional[str]): Sigla da UF para filtrar (opcional)

        Returns:
            List[Dict[str, Any]]: Lista com contagem de participantes por UF

        Exceptions:
            Exception: Erro durante contagem por UF
        """
        try:
            if uf_sigla:
                logger.info(f"Calculando contagem de participantes para UF: {uf_sigla}")
            else:
                logger.info("Calculando contagem de participantes por todas as UFs")

            contagem = await self.participante_repository.get_participantes_por_uf(
                uf_sigla
            )

            logger.info(f"Contagem calculada para {len(contagem)} UF(s)")
            return contagem

        except Exception as e:
            logger.error(f"Erro ao calcular participantes por UF: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def obter_distribuicao_idade(self) -> List[Dict[str, Any]]:
        """
        Obter distribuição de idades dos participantes.

        Args:
            None

        Returns:
            List[Dict[str, Any]]: Distribuição de idades dos participantes

        Exceptions:
            Exception: Erro durante cálculo da distribuição
        """
        try:
            logger.info("Calculando distribuição de idades dos participantes")
            distribuicao = await self.participante_repository.get_distribuicao_idade()

            logger.info(
                f"Distribuição calculada com {len(distribuicao)} faixas etárias"
            )
            return distribuicao

        except Exception as e:
            logger.error(f"Erro ao calcular distribuição de idade: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def obter_participantes_por_escola(
        self, escola_codigo: int
    ) -> List[Dict[str, Any]]:
        """
        Obter participantes de uma escola específica.

        Args:
            escola_codigo (int): Código da escola

        Returns:
            List[Dict[str, Any]]: Lista de participantes da escola

        Exceptions:
            Exception: Erro durante busca dos participantes
        """
        try:
            logger.info(f"Buscando participantes da escola: {escola_codigo}")
            filter_dict = {"escola_codigo": escola_codigo}
            participantes = await self.participante_repository.find_all(
                filter_dict=filter_dict
            )

            logger.info(
                f"Encontrados {len(participantes)} participantes da escola {escola_codigo}"
            )
            return participantes

        except Exception as e:
            logger.error(
                f"Erro ao buscar participantes da escola {escola_codigo}: {str(e)}"
            )
            logger.error(traceback.format_exc())
            raise

    async def atualizar_participante(
        self, participante_id: str, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Atualizar dados de um participante.

        Args:
            participante_id (str): ID do participante
            update_data (Dict[str, Any]): Dados para atualização

        Returns:
            Optional[Dict[str, Any]]: Dados do participante atualizado ou None

        Exceptions:
            Exception: Erro durante atualização do participante
        """
        try:
            logger.info(f"Atualizando participante: {participante_id}")
            resultado = await self.participante_repository.update(
                participante_id, update_data
            )

            if resultado:
                logger.info(f"Participante atualizado com sucesso: {participante_id}")
            else:
                logger.warning(f"Falha ao atualizar participante: {participante_id}")

            return resultado

        except Exception as e:
            logger.error(f"Erro ao atualizar participante {participante_id}: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def deletar_participante(self, participante_id: str) -> bool:
        """
        Excluir um participante.

        Args:
            participante_id (str): ID do participante

        Returns:
            bool: True se excluído com sucesso, False caso contrário

        Exceptions:
            Exception: Erro durante exclusão do participante
        """
        try:
            logger.info(f"Excluindo participante: {participante_id}")
            resultado = await self.participante_repository.delete(participante_id)

            if resultado:
                logger.info(f"Participante excluído com sucesso: {participante_id}")
            else:
                logger.warning(f"Falha ao excluir participante: {participante_id}")

            return resultado

        except Exception as e:
            logger.error(f"Erro ao excluir participante {participante_id}: {str(e)}")
            logger.error(traceback.format_exc())
            raise
