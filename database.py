from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração do MongoDB
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "crm_database")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "crm_records")
CONFIG_COLLECTION_NAME = os.getenv("CONFIG_COLLECTION_NAME", "config")

# Cliente MongoDB global
client: Optional[AsyncIOMotorClient] = None
database = None


async def connect_to_mongo():
    """Conecta ao MongoDB"""
    global client, database
    try:
        client = AsyncIOMotorClient(MONGODB_URL)
        database = client[DATABASE_NAME]
        # Testa a conexão
        await client.admin.command('ping')
        print(f"Conectado ao MongoDB: {DATABASE_NAME}")
        return database
    except Exception as e:
        print(f"Erro ao conectar ao MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Fecha a conexão com o MongoDB"""
    global client
    if client:
        client.close()
        print("Conexão com MongoDB fechada")


def get_database():
    """Retorna a instância do banco de dados"""
    return database


def get_collection():
    """Retorna a collection de registros CRM"""
    if database is None:
        raise Exception("Database não está conectado. Chame connect_to_mongo() primeiro.")
    return database[COLLECTION_NAME]


def get_config_collection():
    """Retorna a collection de configurações"""
    if database is None:
        raise Exception("Database não está conectado. Chame connect_to_mongo() primeiro.")
    return database[CONFIG_COLLECTION_NAME]

