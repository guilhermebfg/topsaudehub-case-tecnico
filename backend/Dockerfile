FROM python:3.11-slim

WORKDIR /app

# deps de sistema para psycopg e compilação eventual
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# instala deps Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copia o projeto do backend para /app/backend
COPY . /app/backend


ENV PYTHONPATH=/app
ENV TZ=America/Sao_Paulo

EXPOSE 8000
