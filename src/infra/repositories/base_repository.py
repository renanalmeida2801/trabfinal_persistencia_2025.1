from abc import ABC
from typing import Any, Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from models.base import MongoBaseModel


class BaseRepository(ABC):
    def __init__(self, database: AsyncIOMotorDatabase, collection_name: str):
        self.database = database
        self.collection = database[collection_name]

    async def create(self, document: MongoBaseModel) -> MongoBaseModel:
        """Criar um novo documento"""
        document_dict = document.dict(by_alias=True)
        result = await self.collection.insert_one(document_dict)
        document.id = result.inserted_id
        return document

    async def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Buscar documento por ID"""
        if not ObjectId.is_valid(id):
            return None
        return await self.collection.find_one({"_id": ObjectId(id)})

    async def find_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filter_dict: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: int = 1,
    ) -> List[Dict[str, Any]]:
        """Buscar todos os documentos com paginação"""
        filter_dict = filter_dict or {}
        cursor = self.collection.find(filter_dict)

        if sort_by:
            cursor = cursor.sort(sort_by, sort_order)

        cursor = cursor.skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    async def count(self, filter_dict: Optional[Dict[str, Any]] = None) -> int:
        """Contar documentos"""
        filter_dict = filter_dict or {}
        return await self.collection.count_documents(filter_dict)

    async def update_by_id(self, id: str, update_dict: Dict[str, Any]) -> bool:
        """Atualizar documento por ID"""
        if not ObjectId.is_valid(id):
            return False
        result = await self.collection.update_one(
            {"_id": ObjectId(id)}, {"$set": update_dict}
        )
        return result.modified_count > 0

    async def delete_by_id(self, id: str) -> bool:
        """Deletar documento por ID"""
        if not ObjectId.is_valid(id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0

    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Executar pipeline de agregação"""
        cursor = self.collection.aggregate(pipeline)
        return await cursor.to_list(length=None)
