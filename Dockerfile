FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# Copia requirements e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o .env para dentro da imagem
COPY .env ./.env

# Copia o restante do código
COPY . .

EXPOSE 3008

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3008"]

