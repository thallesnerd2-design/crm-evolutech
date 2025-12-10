import os
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from models import CRMRecord, ConfigModel
from database import connect_to_mongo, close_mongo_connection, get_collection, get_config_collection
from typing import List, Any, Dict
from bson import ObjectId
from datetime import datetime
import uvicorn


def serialize_mongo_document(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converte um documento do MongoDB para um formato serializável JSON.
    Converte ObjectId para string e datetime para ISO format string.
    """
    if doc is None:
        return None
    
    serialized = {}
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            serialized[key] = str(value)
        elif isinstance(value, datetime):
            serialized[key] = value.isoformat()
        elif isinstance(value, dict):
            serialized[key] = serialize_mongo_document(value)
        elif isinstance(value, list):
            serialized[key] = [
                serialize_mongo_document(item) if isinstance(item, dict) else 
                str(item) if isinstance(item, ObjectId) else
                item.isoformat() if isinstance(item, datetime) else item
                for item in value
            ]
        else:
            serialized[key] = value
    
    return serialized

app = FastAPI(
    title="CRM API",
    description="API para gerenciar registros do CRM no MongoDB",
    version="1.0.0"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_db_client():
    """Conecta ao MongoDB na inicialização da aplicação"""
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_db_client():
    """Fecha a conexão com o MongoDB ao encerrar a aplicação"""
    await close_mongo_connection()



@app.post("/crm/records", status_code=status.HTTP_201_CREATED)
async def create_record(record: CRMRecord):
    """
    Endpoint POST para adicionar um novo registro na collection do MongoDB
    
    Recebe um objeto JSON com todos os campos do CRM e salva no MongoDB
    """
    try:
        collection = get_collection()
        
        # Converte o modelo Pydantic para dict
        record_dict = record.model_dump(exclude_none=True)
        
        # Adiciona timestamp de criação
        record_dict["created_at"] = datetime.utcnow()
        record_dict["updated_at"] = datetime.utcnow()
        
        # Insere o documento no MongoDB
        result = await collection.insert_one(record_dict)
        
        # Busca o documento inserido para retornar completo
        inserted_record = await collection.find_one({"_id": result.inserted_id})
        serialized_record = serialize_mongo_document(inserted_record)
        
        # Retorna o ID do documento criado
        return {
            "message": "Registro criado com sucesso",
            "id": str(result.inserted_id),
            "record": serialized_record
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar registro: {str(e)}"
        )


@app.post("/crm/records/batch", status_code=status.HTTP_201_CREATED)
async def create_records_batch(records: List[CRMRecord]):
    """
    Endpoint POST para adicionar múltiplos registros de uma vez
    
    Recebe uma lista de objetos JSON e salva todos no MongoDB
    """
    try:
        collection = get_collection()
        
        # Converte todos os modelos para dict
        records_dict = []
        for record in records:
            record_dict = record.model_dump(exclude_none=True)
            record_dict["created_at"] = datetime.utcnow()
            record_dict["updated_at"] = datetime.utcnow()
            records_dict.append(record_dict)
        
        # Insere todos os documentos
        result = await collection.insert_many(records_dict)
        
        return {
            "message": f"{len(result.inserted_ids)} registros criados com sucesso",
            "ids": [str(id) for id in result.inserted_ids],
            "count": len(result.inserted_ids)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar registros: {str(e)}"
        )


@app.get("/crm/records")
async def get_all_records(skip: int = 0, limit: int = 100):
    """
    Endpoint GET para listar todos os registros
    
    Parâmetros:
    - skip: Número de registros para pular (paginação)
    - limit: Número máximo de registros para retornar
    """
    try:
        collection = get_collection()
        
        # Busca todos os registros
        cursor = collection.find().skip(skip).limit(limit)
        records = await cursor.to_list(length=limit)
        
        # Serializa todos os registros (converte ObjectId e datetime)
        serialized_records = [serialize_mongo_document(record) for record in records]
        
        # Conta o total de registros
        total = await collection.count_documents({})
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "records": serialized_records
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar registros: {str(e)}"
        )


@app.get("/crm/records/{record_id}")
async def get_record_by_id(record_id: str):
    """
    Endpoint GET para buscar um registro específico por ID
    """
    try:
        collection = get_collection()
        
        # Valida se o ObjectId é válido
        try:
            object_id = ObjectId(record_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID inválido. O ID deve ser um ObjectId válido do MongoDB."
            )
        
        # Busca o registro por ID
        record = await collection.find_one({"_id": object_id})
        
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registro não encontrado"
            )
        
        # Serializa o registro (converte ObjectId e datetime)
        serialized_record = serialize_mongo_document(record)
        
        return serialized_record
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar registro: {str(e)}"
        )


@app.put("/crm/records/{record_id}")
async def update_record(record_id: str, record: CRMRecord):
    """
    Endpoint PUT para atualizar um registro existente na collection do MongoDB
    
    Recebe um objeto JSON com os campos a serem atualizados e atualiza o registro pelo ID
    """
    try:
        collection = get_collection()
        
        # Valida se o ObjectId é válido
        try:
            object_id = ObjectId(record_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID inválido. O ID deve ser um ObjectId válido do MongoDB."
            )
        
        # Verifica se o registro existe
        existing_record = await collection.find_one({"_id": object_id})
        if existing_record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registro não encontrado"
            )
        
        # Converte o modelo Pydantic para dict
        record_dict = record.model_dump(exclude_none=True)
        
        # Adiciona/atualiza timestamp de atualização
        record_dict["updated_at"] = datetime.utcnow()
        
        # Preserva o created_at original se existir
        if "created_at" not in record_dict and "created_at" in existing_record:
            record_dict["created_at"] = existing_record["created_at"]
        
        # Atualiza o documento no MongoDB
        result = await collection.update_one(
            {"_id": object_id},
            {"$set": record_dict}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhuma alteração foi feita no registro"
            )
        
        # Busca o registro atualizado
        updated_record = await collection.find_one({"_id": object_id})
        serialized_record = serialize_mongo_document(updated_record)
        
        return {
            "message": "Registro atualizado com sucesso",
            "id": record_id,
            "record": serialized_record
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar registro: {str(e)}"
        )


@app.delete("/crm/records/{record_id}")
async def delete_record(record_id: str):
    """
    Endpoint DELETE para deletar um registro da collection do MongoDB
    
    Remove o registro pelo ID fornecido
    """
    try:
        collection = get_collection()
        
        # Valida se o ObjectId é válido
        try:
            object_id = ObjectId(record_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID inválido. O ID deve ser um ObjectId válido do MongoDB."
            )
        
        # Verifica se o registro existe antes de deletar
        existing_record = await collection.find_one({"_id": object_id})
        if existing_record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registro não encontrado"
            )
        
        # Serializa o registro antes de deletar para retornar
        serialized_record = serialize_mongo_document(existing_record)
        
        # Deleta o documento do MongoDB
        result = await collection.delete_one({"_id": object_id})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao deletar registro"
            )
        
        return {
            "message": "Registro deletado com sucesso",
            "id": record_id,
            "deleted_record": serialized_record
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar registro: {str(e)}"
        )


# ==================== ENDPOINTS DE CONFIGURAÇÃO ====================

@app.get("/config")
async def get_config():
    """
    Endpoint GET para obter as configurações do sistema
    
    Retorna a estrutura de configuração com:
    - consultor: array de objetos {name, equipe}
    - status: array de strings
    - servicos: array de strings
    - plano: array de objetos {name, value}
    - pacote_sva: array de strings
    """
    try:
        collection = get_config_collection()
        
        # Busca a configuração (assumindo que há apenas um documento de configuração)
        config = await collection.find_one({})
        
        # Se não existir, retorna estrutura vazia
        if config is None:
            return {
                "consultor": [],
                "status": [],
                "servicos": [],
                "plano": [],
                "pacote_sva": []
            }
        
        # Remove o _id e serializa
        config.pop("_id", None)
        serialized_config = serialize_mongo_document(config)
        
        return serialized_config
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar configuração: {str(e)}"
        )


@app.post("/config", status_code=status.HTTP_201_CREATED)
async def create_config(config: ConfigModel):
    """
    Endpoint POST para criar/atualizar as configurações do sistema
    
    Se já existir uma configuração, ela será substituída.
    Recebe um objeto JSON com a estrutura de configuração completa.
    """
    try:
        collection = get_config_collection()
        
        # Converte o modelo Pydantic para dict
        config_dict = config.model_dump(exclude_none=True)
        
        # Adiciona timestamp
        config_dict["created_at"] = datetime.utcnow()
        config_dict["updated_at"] = datetime.utcnow()
        
        # Verifica se já existe uma configuração
        existing_config = await collection.find_one({})
        
        if existing_config:
            # Atualiza a configuração existente
            config_dict["created_at"] = existing_config.get("created_at", datetime.utcnow())
            result = await collection.replace_one({}, config_dict)
            
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Erro ao atualizar configuração"
                )
            
            message = "Configuração atualizada com sucesso"
        else:
            # Insere nova configuração
            result = await collection.insert_one(config_dict)
            message = "Configuração criada com sucesso"
        
        # Busca a configuração atualizada/criada
        updated_config = await collection.find_one({})
        updated_config.pop("_id", None)
        serialized_config = serialize_mongo_document(updated_config)
        
        return {
            "message": message,
            "config": serialized_config
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar configuração: {str(e)}"
        )


@app.put("/config")
async def update_config(config: ConfigModel):
    """
    Endpoint PUT para atualizar as configurações do sistema
    
    Atualiza a configuração existente. Se não existir, retorna erro 404.
    """
    try:
        collection = get_config_collection()
        
        # Verifica se a configuração existe
        existing_config = await collection.find_one({})
        if existing_config is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuração não encontrada. Use POST para criar uma nova configuração."
            )
        
        # Converte o modelo Pydantic para dict
        config_dict = config.model_dump(exclude_none=True)
        
        # Preserva created_at e atualiza updated_at
        config_dict["created_at"] = existing_config.get("created_at", datetime.utcnow())
        config_dict["updated_at"] = datetime.utcnow()
        
        # Atualiza a configuração
        result = await collection.replace_one({}, config_dict)
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhuma alteração foi feita na configuração"
            )
        
        # Busca a configuração atualizada
        updated_config = await collection.find_one({})
        updated_config.pop("_id", None)
        serialized_config = serialize_mongo_document(updated_config)
        
        return {
            "message": "Configuração atualizada com sucesso",
            "config": serialized_config
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar configuração: {str(e)}"
        )


@app.delete("/config")
async def delete_config():
    """
    Endpoint DELETE para deletar as configurações do sistema
    
    Remove a configuração do banco de dados.
    """
    try:
        collection = get_config_collection()
        
        # Verifica se a configuração existe
        existing_config = await collection.find_one({})
        if existing_config is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuração não encontrada"
            )
        
        # Serializa a configuração antes de deletar
        existing_config.pop("_id", None)
        serialized_config = serialize_mongo_document(existing_config)
        
        # Deleta a configuração
        result = await collection.delete_one({})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao deletar configuração"
            )
        
        return {
            "message": "Configuração deletada com sucesso",
            "deleted_config": serialized_config
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar configuração: {str(e)}"
        )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "3002"))
    uvicorn.run(app, host="0.0.0.0", port=port)

