import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional

from config.logs import logger
from infra.repositories.municipio_repository import MunicipioRepository
from models.municipio import Municipio


class MunicipioService:
    def __init__(self, municipio_repository: MunicipioRepository):
        """
        Inicializar o service de municípios.
        
        Args:
            municipio_repository (MunicipioRepository): Repository para operações de município
            
        Returns:
            None
            
        Exceptions:
            None
        """
        self.municipio_repository = municipio_repository

    async def criar_municipio(self, municipio_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Criar um novo município.
        
        Args:
            municipio_data (Dict[str, Any]): Dados do município a ser criado
            
        Returns:
            Dict[str, Any]: Dados do município criado
            
        Exceptions:
            Exception: Erro durante criação do município
        """
        try:
            nome_municipio = municipio_data.get('nome', 'N/A')
            logger.info(f"Criando município: {nome_municipio}")
            
            municipio = Municipio(**municipio_data)
            created_municipio = await self.municipio_repository.create(municipio)
            
            logger.info(f"Município criado com sucesso - ID: {created_municipio.id}, Nome: {nome_municipio}")
            return created_municipio.dict()
            
        except Exception as e:
            logger.error(f"Erro ao criar município: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def obter_municipio_por_id(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Obter município por ID.
        
        Args:
            id (str): ID do município
            
        Returns:
            Optional[Dict[str, Any]]: Dados do município encontrado ou None
            
        Exceptions:
            Exception: Erro durante busca do município
        """
        try:
            logger.info(f"Buscando município por ID: {id}")
            resultado = await self.municipio_repository.find_by_id(id)
            
            if resultado:
                logger.info(f"Município encontrado: {resultado.get('nome', 'N/A')}")
            else:
                logger.warning(f"Município não encontrado para ID: {id}")
                
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao buscar município por ID {id}: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def obter_municipio_por_codigo(self, codigo: int) -> Optional[Dict[str, Any]]:
        """
        Obter município por código.
        
        Args:
            codigo (int): Código do município
            
        Returns:
            Optional[Dict[str, Any]]: Dados do município encontrado ou None
            
        Exceptions:
            Exception: Erro durante busca do município
        """
        try:
            logger.info(f"Buscando município por código: {codigo}")
            resultado = await self.municipio_repository.find_by_codigo(codigo)
            
            if resultado:
                logger.info(f"Município encontrado: {resultado.get('nome', 'N/A')}")
            else:
                logger.warning(f"Município não encontrado para código: {codigo}")
                
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao buscar município por código {codigo}: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def listar_municipios(
        self,
        skip: int = 0,
        limit: int = 100,
        uf_sigla: Optional[str] = None,
        regiao: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Listar municípios com filtros opcionais.
        
        Args:
            skip (int): Número de registros a pular. Default: 0
            limit (int): Limite de registros retornados. Default: 100
            uf_sigla (Optional[str]): Filtrar por sigla da UF. Default: None
            regiao (Optional[str]): Filtrar por região. Default: None
            
        Returns:
            Dict[str, Any]: Dados paginados dos municípios com metadados
            
        Exceptions:
            Exception: Erro durante listagem dos municípios
        """
        try:
            logger.info(f"Listando municípios - skip: {skip}, limit: {limit}, filtros: uf_sigla={uf_sigla}, regiao={regiao}")
            
            filter_dict = {}
            if uf_sigla:
                filter_dict["uf_sigla"] = uf_sigla
            if regiao:
                filter_dict["regiao"] = regiao

            municipios = await self.municipio_repository.find_all(
                skip=skip, limit=limit, filter_dict=filter_dict, sort_by="nome"
            )
            total = await self.municipio_repository.count(filter_dict)

            logger.info(f"Encontrados {total} municípios, retornando {len(municipios)} registros")
            
            return {
                "items": municipios,
                "total": total,
                "skip": skip,
                "limit": limit,
                "has_more": skip + limit < total,
            }
            
        except Exception as e:
            logger.error(f"Erro ao listar municípios: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def atualizar_municipio(self, id: str, update_data: Dict[str, Any]) -> bool:
        """
        Atualizar município.
        
        Args:
            id (str): ID do município
            update_data (Dict[str, Any]): Dados para atualização
            
        Returns:
            bool: True se atualizado com sucesso, False caso contrário
            
        Exceptions:
            Exception: Erro durante atualização do município
        """
        try:
            logger.info(f"Atualizando município ID: {id}")
            update_data["updated_at"] = datetime.now()
            result = await self.municipio_repository.update_by_id(id, update_data)
            
            if result:
                logger.info(f"Município atualizado com sucesso: {id}")
            else:
                logger.warning(f"Falha ao atualizar município: {id}")
                
            return result
            
        except Exception as e:
            logger.error(f"Erro ao atualizar município {id}: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def deletar_municipio(self, id: str) -> bool:
        """
        Deletar município.
        
        Args:
            id (str): ID do município
            
        Returns:
            bool: True se deletado com sucesso, False caso contrário
            
        Exceptions:
            Exception: Erro durante deleção do município
        """
        try:
            logger.info(f"Deletando município ID: {id}")
            result = await self.municipio_repository.delete_by_id(id)
            
            if result:
                logger.info(f"Município deletado com sucesso: {id}")
            else:
                logger.warning(f"Falha ao deletar município: {id}")
                
            return result
            
        except Exception as e:
            logger.error(f"Erro ao deletar município {id}: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def obter_estatisticas_por_regiao(self) -> List[Dict[str, Any]]:
        """
        Obter estatísticas agrupadas por região.
        
        Args:
            None
            
        Returns:
            List[Dict[str, Any]]: Lista com estatísticas por região
            
        Exceptions:
            Exception: Erro durante cálculo das estatísticas
        """
        try:
            logger.info("Calculando estatísticas por região")
            estatisticas = await self.municipio_repository.get_estatisticas_por_regiao()
            
            logger.info(f"Estatísticas calculadas para {len(estatisticas)} regiões")
            return estatisticas
            
        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas por região: {str(e)}")
            logger.error(traceback.format_exc())
            raise
