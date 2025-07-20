import traceback
from typing import Any, Dict, List, Optional

from config.logs import logger
from infra.repositories.escola_repository import EscolaRepository
from models.escola import Escola


class EscolaService:
    def __init__(self, escola_repository: EscolaRepository):
        """
        Inicializar o service de escolas.

        Args:
            escola_repository (EscolaRepository): Repository para operações de escola

        Returns:
            None

        Exceptions:
            None
        """
        self.escola_repository = escola_repository

    async def criar_escola(self, escola_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Criar uma nova escola.

        Args:
            escola_data (Dict[str, Any]): Dados da escola a ser criada

        Returns:
            Dict[str, Any]: Dados da escola criada

        Exceptions:
            Exception: Erro durante criação da escola
        """
        try:
            codigo_escola = escola_data.get("codigo", "N/A")
            nome_escola = escola_data.get("nome", "N/A")
            logger.info(f"Criando escola: {codigo_escola} - {nome_escola}")

            escola = Escola(**escola_data)
            created_escola = await self.escola_repository.create(escola)

            logger.info(f"Escola criada com sucesso: {codigo_escola}")
            return created_escola.dict()

        except Exception as e:
            logger.error(f"Erro ao criar escola: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def obter_escola_por_id(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Obter escola por ID.

        Args:
            id (str): ID da escola

        Returns:
            Optional[Dict[str, Any]]: Dados da escola encontrada ou None

        Exceptions:
            Exception: Erro durante busca da escola
        """
        try:
            logger.info(f"Buscando escola por ID: {id}")
            resultado = await self.escola_repository.find_by_id(id)

            if resultado:
                logger.info(f"Escola encontrada: {resultado.get('nome', 'N/A')}")
            else:
                logger.warning(f"Escola não encontrada para ID: {id}")

            return resultado

        except Exception as e:
            logger.error(f"Erro ao buscar escola por ID {id}: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def obter_escola_por_codigo(self, codigo: int) -> Optional[Dict[str, Any]]:
        """
        Obter escola por código.

        Args:
            codigo (int): Código da escola

        Returns:
            Optional[Dict[str, Any]]: Dados da escola encontrada ou None

        Exceptions:
            Exception: Erro durante busca da escola
        """
        try:
            logger.info(f"Buscando escola por código: {codigo}")
            resultado = await self.escola_repository.find_by_codigo(codigo)

            if resultado:
                logger.info(f"Escola encontrada: {resultado.get('nome', 'N/A')}")
            else:
                logger.warning(f"Escola não encontrada para código: {codigo}")

            return resultado

        except Exception as e:
            logger.error(f"Erro ao buscar escola por código {codigo}: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def listar_escolas(
        self,
        skip: int = 0,
        limit: int = 100,
        uf: Optional[str] = None,
        municipio: Optional[str] = None,
        dependencia_administrativa: Optional[str] = None,
        localizacao: Optional[str] = None,
        situacao_funcionamento: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Listar escolas com filtros opcionais.

        Args:
            skip (int): Número de registros a pular. Default: 0
            limit (int): Limite de registros retornados. Default: 100
            uf (Optional[str]): Filtrar por UF. Default: None
            municipio (Optional[str]): Filtrar por município. Default: None
            dependencia_administrativa (Optional[str]): Filtrar por dependência administrativa. Default: None
            localizacao (Optional[str]): Filtrar por localização. Default: None
            situacao_funcionamento (Optional[str]): Filtrar por situação de funcionamento. Default: None

        Returns:
            Dict[str, Any]: Dados paginados das escolas com metadados

        Exceptions:
            Exception: Erro durante listagem das escolas
        """
        try:
            filtros_str = f"skip={skip}, limit={limit}, uf={uf}, municipio={municipio}, dependencia_administrativa={dependencia_administrativa}, localizacao={localizacao}, situacao_funcionamento={situacao_funcionamento}"
            logger.info(f"Listando escolas - {filtros_str}")

            filter_dict = {}
            if uf:
                filter_dict["uf"] = uf
            if municipio:
                filter_dict["municipio"] = municipio
            if dependencia_administrativa:
                filter_dict["dependencia_administrativa"] = dependencia_administrativa
            if localizacao:
                filter_dict["localizacao"] = localizacao
            if situacao_funcionamento:
                filter_dict["situacao_funcionamento"] = situacao_funcionamento

            escolas = await self.escola_repository.find_all(
                skip=skip, limit=limit, filter_dict=filter_dict, sort_by="nome"
            )
            total = await self.escola_repository.count(filter_dict)

            logger.info(
                f"Encontradas {total} escolas, retornando {len(escolas)} registros"
            )

            return {
                "items": escolas,
                "total": total,
                "skip": skip,
                "limit": limit,
                "has_more": skip + limit < total,
            }

        except Exception as e:
            logger.error(f"Erro ao listar escolas: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def obter_escolas_por_uf(self) -> List[Dict[str, Any]]:
        """
        Obter contagem de escolas por UF.

        Args:
            None

        Returns:
            List[Dict[str, Any]]: Lista com contagem de escolas por UF

        Exceptions:
            Exception: Erro durante contagem por UF
        """
        try:
            logger.info("Calculando contagem de escolas por UF")
            contagem = await self.escola_repository.get_escolas_por_uf()

            logger.info(f"Contagem calculada para {len(contagem)} UFs")
            return contagem

        except Exception as e:
            logger.error(f"Erro ao calcular escolas por UF: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def obter_escolas_por_dependencia(self) -> List[Dict[str, Any]]:
        """
        Obter distribuição de escolas por dependência administrativa.

        Args:
            None

        Returns:
            List[Dict[str, Any]]: Distribuição de escolas por dependência administrativa

        Exceptions:
            Exception: Erro durante cálculo da distribuição
        """
        try:
            logger.info(
                "Calculando distribuição de escolas por dependência administrativa"
            )
            distribuicao = await self.escola_repository.get_escolas_por_dependencia()

            logger.info(
                f"Distribuição calculada com {len(distribuicao)} tipos de dependência"
            )
            return distribuicao

        except Exception as e:
            logger.error(f"Erro ao calcular distribuição por dependência: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def obter_escolas_por_localizacao(self) -> List[Dict[str, Any]]:
        """
        Obter distribuição de escolas por localização (urbana/rural).

        Args:
            None

        Returns:
            List[Dict[str, Any]]: Distribuição de escolas por localização

        Exceptions:
            Exception: Erro durante cálculo da distribuição
        """
        try:
            logger.info("Calculando distribuição de escolas por localização")
            distribuicao = await self.escola_repository.get_escolas_por_localizacao()

            logger.info(
                f"Distribuição calculada com {len(distribuicao)} tipos de localização"
            )
            return distribuicao

        except Exception as e:
            logger.error(f"Erro ao calcular distribuição por localização: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def obter_ranking_escolas_por_desempenho(
        self, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Obter ranking de escolas por desempenho médio dos participantes.

        Args:
            limit (int): Número máximo de escolas no ranking. Default: 50

        Returns:
            List[Dict[str, Any]]: Lista com ranking das escolas

        Exceptions:
            Exception: Erro durante geração do ranking
        """
        try:
            logger.info(f"Gerando ranking de escolas por desempenho (top {limit})")
            ranking = await self.escola_repository.get_ranking_por_desempenho(limit)

            logger.info(f"Ranking gerado com {len(ranking)} escolas")
            return ranking

        except Exception as e:
            logger.error(f"Erro ao gerar ranking de escolas: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def obter_estatisticas_escola(self, codigo: int) -> Dict[str, Any]:
        """
        Obter estatísticas detalhadas de uma escola específica.

        Args:
            codigo (int): Código da escola

        Returns:
            Dict[str, Any]: Dados da escola com estatísticas ou dict vazio

        Exceptions:
            Exception: Erro durante busca das estatísticas
        """
        try:
            logger.info(f"Buscando estatísticas da escola: {codigo}")
            escola = await self.escola_repository.find_by_codigo(codigo)

            if not escola:
                logger.warning(f"Escola não encontrada para código: {codigo}")
                return {}

            stats = await self.escola_repository.get_estatisticas_escola(codigo)
            resultado = {
                "escola": escola,
                "estatisticas": stats,
            }

            logger.info(f"Estatísticas obtidas para escola: {codigo}")
            return resultado

        except Exception as e:
            logger.error(f"Erro ao buscar estatísticas da escola {codigo}: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def atualizar_escola(
        self, escola_id: str, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Atualizar dados de uma escola.

        Args:
            escola_id (str): ID da escola
            update_data (Dict[str, Any]): Dados para atualização

        Returns:
            Optional[Dict[str, Any]]: Dados da escola atualizada ou None

        Exceptions:
            Exception: Erro durante atualização da escola
        """
        try:
            logger.info(f"Atualizando escola: {escola_id}")
            resultado = await self.escola_repository.update(escola_id, update_data)

            if resultado:
                logger.info(f"Escola atualizada com sucesso: {escola_id}")
            else:
                logger.warning(f"Falha ao atualizar escola: {escola_id}")

            return resultado

        except Exception as e:
            logger.error(f"Erro ao atualizar escola {escola_id}: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def excluir_escola(self, escola_id: str) -> bool:
        """
        Excluir uma escola.

        Args:
            escola_id (str): ID da escola

        Returns:
            bool: True se excluída com sucesso, False caso contrário

        Exceptions:
            Exception: Erro durante exclusão da escola
        """
        try:
            logger.info(f"Excluindo escola: {escola_id}")
            resultado = await self.escola_repository.delete(escola_id)

            if resultado:
                logger.info(f"Escola excluída com sucesso: {escola_id}")
            else:
                logger.warning(f"Falha ao excluir escola: {escola_id}")

            return resultado

        except Exception as e:
            logger.error(f"Erro ao excluir escola {escola_id}: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def buscar_escolas_por_nome(
        self, nome: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Buscar escolas por nome (busca parcial).

        Args:
            nome (str): Nome ou parte do nome da escola
            limit (int): Limite de resultados. Default: 20

        Returns:
            List[Dict[str, Any]]: Lista de escolas encontradas

        Exceptions:
            Exception: Erro durante busca das escolas
        """
        try:
            logger.info(f"Buscando escolas por nome: '{nome}' (limite: {limit})")
            filter_dict = {"nome": {"$regex": nome, "$options": "i"}}
            escolas = await self.escola_repository.find_all(
                limit=limit, filter_dict=filter_dict, sort_by="nome"
            )

            logger.info(
                f"Encontradas {len(escolas)} escolas com nome similar a '{nome}'"
            )
            return escolas

        except Exception as e:
            logger.error(f"Erro ao buscar escolas por nome '{nome}': {str(e)}")
            logger.error(traceback.format_exc())
            raise
