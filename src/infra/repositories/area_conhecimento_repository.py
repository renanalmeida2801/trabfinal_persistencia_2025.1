from typing import Optional, Dict, Any, List
from infra.repositories.base_repository import BaseRepository
from models.area_conhecimento import AreaConhecimento
from utils.json_utils import serialize_mongo_document


class AreaConhecimentoRepository(BaseRepository):
    def __init__(self, database):
        super().__init__(database, "areas_conhecimento")

    async def find_by_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        """Buscar área por código"""
        try:
            result = await self.collection.find_one({"codigo": codigo})
            return serialize_mongo_document(result)
        except Exception as e:
            print(f"Erro ao buscar área por código: {e}")
            return None

    async def find_all_active(self) -> List[Dict[str, Any]]:
        """Buscar todas as áreas ativas"""
        try:
            cursor = self.collection.find({"ativa": True})
            result = await cursor.to_list(length=None)
            return serialize_mongo_document(result)
        except Exception as e:
            print(f"Erro ao buscar áreas ativas: {e}")
            return []

    async def create_area(self, area_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Criar nova área de conhecimento"""
        try:
            area = AreaConhecimento(**area_data)
            result = await self.collection.insert_one(area.model_dump(by_alias=True))

            # Buscar o documento inserido
            created_area = await self.collection.find_one({"_id": result.inserted_id})
            return serialize_mongo_document(created_area)
        except Exception as e:
            print(f"Erro ao criar área: {e}")
            raise

    async def find_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filter_dict: Optional[Dict[str, Any]] = None,
        sort_by: str = "codigo",
    ) -> List[Dict[str, Any]]:
        """Buscar áreas com filtros e paginação"""
        try:
            filter_dict = filter_dict or {}

            cursor = self.collection.find(filter_dict).skip(skip).limit(limit)

            if sort_by:
                cursor = cursor.sort(sort_by, 1)

            result = await cursor.to_list(length=limit)
            return serialize_mongo_document(result)
        except Exception as e:
            print(f"Erro ao buscar áreas: {e}")
            return []

    async def count(self, filter_dict: Optional[Dict[str, Any]] = None) -> int:
        """Contar áreas com filtro"""
        try:
            filter_dict = filter_dict or {}
            return await self.collection.count_documents(filter_dict)
        except Exception as e:
            print(f"Erro ao contar áreas: {e}")
            return 0

    async def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Buscar área por ID"""
        try:
            from bson import ObjectId

            result = await self.collection.find_one({"_id": ObjectId(id)})
            return serialize_mongo_document(result)
        except Exception as e:
            print(f"Erro ao buscar área por ID: {e}")
            return None

    async def update(
        self, id: str, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Atualizar área"""
        try:
            from bson import ObjectId

            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(id)}, {"$set": update_data}, return_document=True
            )
            return serialize_mongo_document(result)
        except Exception as e:
            print(f"Erro ao atualizar área: {e}")
            return None

    async def delete(self, id: str) -> bool:
        """Deletar área"""
        try:
            from bson import ObjectId

            result = await self.collection.delete_one({"_id": ObjectId(id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Erro ao deletar área: {e}")
            return False
