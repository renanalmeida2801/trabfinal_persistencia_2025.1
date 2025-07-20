from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

from config.logs import logger
from config.settings import settings


class Database:
    client: AsyncIOMotorClient = None
    database = None


db = Database()


async def get_database() -> AsyncIOMotorClient:
    return db.database


async def connect_to_mongo():
    """Criar conexão com MongoDB"""
    logger.info("Conectando ao MongoDB...")
    db.client = AsyncIOMotorClient(settings.MONGO_URL)
    db.database = db.client[settings.DATABASE_NAME]
    logger.info(f"Conectado ao MongoDB no banco de dados: {settings.DATABASE_NAME}")


async def close_mongo_connection():
    """Fechar conexão com MongoDB"""
    logger.info("Fechando conexão com MongoDB...")
    if db.client:
        db.client.close()
        logger.info("Conexão com MongoDB fechada.")


def get_sync_database():
    """Conexão síncrona para operações de migração/carregamento de dados"""
    logger.info("Conectando ao MongoDB (síncrono)...")
    client = MongoClient(settings.MONGO_URL)
    logger.info(f"Conectado ao MongoDB no banco de dados: {settings.DATABASE_NAME}")
    return client[settings.DATABASE_NAME]
