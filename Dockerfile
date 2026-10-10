# Usa uma imagem oficial do Python leve
FROM python:3.10-slim

# Evita a criação de arquivos .pyc e garante que os logs apareçam na hora
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define a pasta de trabalho dentro do container
WORKDIR /app

# Copia e instala apenas as dependências primeiro (otimiza o cache do Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o restante do código do projeto para dentro do container
COPY . .

# Comando padrão a ser executado
CMD ["python", "main.py"]