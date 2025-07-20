from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

from config.settings import settings


class Database:
    client: AsyncIOMotorClient = None
    database = None


db = Database()


async def get_database() -> AsyncIOMotorClient:
    return db.database


async def connect_to_mongo():
    """Criar conexão com MongoDB"""
    db.client = AsyncIOMotorClient(settings.MONGO_URL)
    db.database = db.client[settings.DATABASE_NAME]
    print("Conectado ao MongoDB!")


async def close_mongo_connection():
    """Fechar conexão com MongoDB"""
    if db.client:
        db.client.close()
        print("Desconectado do MongoDB!")


def get_sync_database():
    """Conexão síncrona para operações de migração/carregamento de dados"""
    client = MongoClient(settings.MONGO_URL)
    return client[settings.DATABASE_NAME]
