from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CRMRecord(BaseModel):
    """Modelo para os registros do CRM com todas as colunas especificadas"""
    
    uf: Optional[str] = Field(None, description="UF")
    ddd: Optional[str] = Field(None, description="DDD")
    adabas: Optional[str] = Field(None, description="ADABAS")
    responsavel_p_colocar_na_planilha: Optional[str] = Field(None, description="RESPONSAVEL")
    data_entrega: Optional[str] = Field(None, description="DATA RECEBIMENTO")
    crm: Optional[str] = Field(None, description="CRM")
    simulacao: Optional[str] = Field(None, description="SIMULAÇÃO")
    pedido: Optional[str] = Field(None, description="PEDIDO")
    razao_social: Optional[str] = Field(None, description="RAZÃO SOCIAL")
    cnpj: Optional[str] = Field(None, description="CNPJ")
    servicos: Optional[str] = Field(None, description="SERVIÇOS")
    plano: Optional[str] = Field(None, description="PLANO")
    valor_do_plano: Optional[float] = Field(None, description="VALOR DO PLANO")
    quantidade_aparelho: Optional[int] = Field(None, description="QTD APARELHO")
    valor_do_aparelho: Optional[float] = Field(None, description="VALOR DO APARELHO")
    qtd_sva: Optional[int] = Field(None, description="QTD SVA")
    pacote_sva: Optional[str] = Field(None, description="PACOTE SVA")
    valor_sva: Optional[float] = Field(None, description="VALOR SVA")
    valor_atual: Optional[float] = Field(None, description="VALOR ATUAL")
    valor_da_renovacao: Optional[float] = Field(None, description="VALOR DA RENOVAÇÃO")
    m: Optional[str] = Field(None, description="M")
    migracao: Optional[str] = Field(None, description="TIPO DEMIGRAÇÃO")
    base_fresh: Optional[str] = Field(None, description="BASE/FRESH")
    qtd: Optional[int] = Field(None, description="QTD")
    status: Optional[str] = Field(None, description="STATUS")
    data_do_status: Optional[str] = Field(None, description="DATA DO STATUS")
    historico: Optional[str] = Field(None, description="HISTÓRICO")
    consultor: Optional[str] = Field(None, description="CONSULTOR")
    equipe: Optional[str] = Field(None, description="EQUIPE")
    
    class Config:
        json_schema_extra = {
            "example": {
                "uf": "SP",
                "ddd": "11",
                "adabas": "12345",
                "responsavel_p_colocar_na_planilha": "João Silva",
                "data_entrega": "2024-01-15",
                "crm": "CRM001",
                "simulacao": "SIM001",
                "pedido": "PED001",
                "razao_social": "Empresa Exemplo Ltda",
                "cnpj": "12.345.678/0001-90",
                "servicos": "Internet + Telefone",
                "plano": "Plano Premium",
                "valor_do_plano": 299.90,
                "quantidade_aparelho": 2,
                "valor_do_aparelho": 150.00,
                "qtd_sva": 3,
                "pacote_sva": "Pacote Completo",
                "valor_sva": 99.90,
                "valor_atual": 549.80,
                "valor_da_renovacao": 599.90,
                "m": "M",
                "migracao": 18,
                "base_fresh": "base",
                "qtd": 5,
                "status": "Ativo",
                "data_do_status": "2024-01-10",
                "historico": "Cliente migrado em janeiro",
                "consultor": "Maria Santos",
                "equipe": "Equipe A"
            }
        }


# Modelos para Configuração
class PlanoItem(BaseModel):
    """Modelo para item de plano"""
    name: str = Field(..., description="Nome do plano")
    value: float = Field(..., description="Valor do plano")


class ConsultorItem(BaseModel):
    """Modelo para item de consultor"""
    name: str = Field(..., description="Nome do consultor")
    equipe: str = Field(..., description="Nome da equipe")


class ConfigModel(BaseModel):
    """Modelo para configurações do sistema"""
    consultor: List[ConsultorItem] = Field(default_factory=list, description="Lista de consultores")
    status: List[str] = Field(default_factory=list, description="Lista de status")
    servicos: List[str] = Field(default_factory=list, description="Lista de serviços")
    plano: List[PlanoItem] = Field(default_factory=list, description="Lista de planos")
    pacote_sva: List[str] = Field(default_factory=list, description="Lista de pacotes SVA")
    
    class Config:
        json_schema_extra = {
            "example": {
                "consultor": [
                    {"name": "João Silva", "equipe": "Equipe A"},
                    {"name": "Maria Santos", "equipe": "Equipe B"}
                ],
                "status": ["Ativo", "Inativo", "Pendente"],
                "servicos": ["Internet", "Telefone", "TV"],
                "plano": [
                    {"name": "Plano Básico", "value": 99.90},
                    {"name": "Plano Premium", "value": 199.90}
                ],
                "pacote_sva": ["Pacote Completo", "Pacote Básico"]
            }
        }

