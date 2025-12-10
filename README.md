# API CRM - Sistema de Gerenciamento de Registros

API FastAPI para gerenciar registros do CRM no MongoDB.

## Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure as variáveis de ambiente:
   - Copie o arquivo `.env.example` para `.env`
   - Edite o arquivo `.env` com suas configurações do MongoDB

## Executar a aplicação

```bash
python main.py
```

Ou usando uvicorn diretamente:
```bash
uvicorn main:app --reload
```

A API estará disponível em: `http://localhost:8000`

## Documentação

Após iniciar a aplicação, acesse:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

### POST `/crm/records`
Adiciona um novo registro na collection.

**Exemplo de requisição:**
```json
{
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
  "migracao": "SIM",
  "base_fresh": "base",
  "qtd": 5,
  "status": "Ativo",
  "data_do_status": "2024-01-10",
  "historico": "Cliente migrado em janeiro",
  "consultor": "Maria Santos",
  "equipe": "Equipe A"
}
```

### POST `/crm/records/batch`
Adiciona múltiplos registros de uma vez.

**Exemplo de requisição:**
```json
[
  {
    "uf": "SP",
    "ddd": "11",
    "crm": "CRM001",
    ...
  },
  {
    "uf": "RJ",
    "ddd": "21",
    "crm": "CRM002",
    ...
  }
]
```

### GET `/crm/records`
Lista todos os registros (com paginação).

**Parâmetros de query:**
- `skip`: Número de registros para pular (padrão: 0)
- `limit`: Número máximo de registros (padrão: 100)

### GET `/crm/records/{record_id}`
Busca um registro específico por ID.

## Estrutura do Projeto

- `main.py`: Aplicação FastAPI com os endpoints
- `models.py`: Modelos Pydantic para validação dos dados
- `database.py`: Configuração e conexão com MongoDB
- `requirements.txt`: Dependências do projeto

## Campos do Modelo

O modelo inclui todos os campos especificados:
- UF, DDD, ADABAS
- RESPONSAVEL P COLOCAR NA PLANILHA
- DATA ENTREGA, CRM, SIMULAÇÃO, PEDIDO
- RAZÃO SOCIAL, CNPJ, SERVIÇOS, PLANO
- VALOR DO PLANO, QUATIDADE APARELHO, VALOR DO APARELHO
- QTD SVA, PACOTE SVA, VALOR SVA
- VALOR ATUAL, VALOR DA RENOVAÇÃO
- M, MIGRAÇÃO, base/fresh, QTD
- STATUS, DATA DO STATUS, HISTÓRICO
- CONSULTOR, EQUIPE

