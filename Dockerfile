FROM python:3.10-slim

# Metadados e variáveis de ambiente
LABEL maintainer="Equipe 03 - Suprimentos LG Electronics" \
      description="Container de automacao de MRP em Suprimentos"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=America/Manaus \
    DEBIAN_FRONTEND=noninteractive \
    SOURCE_DIR=/app/Source \
    OUTPUT_DIR=/app/output \
    ALERT_FILE=/app/logs/alerts.jsonl \
    GRP_USER=aluno \
    GRP_PASSWORD=avaliacao2026 \
    GRP_URL=http://grp-web:8000/web/grp_fake.html

WORKDIR /app

# Instalar dependências do sistema e configurar fuso horário de Manaus
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    curl \
    ca-certificates \
    && ln -fs /usr/share/zoneinfo/$TZ /etc/localtime \
    && dpkg-reconfigure -f noninteractive tzdata \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependências Python e navegador Playwright com dependências de sistema
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && playwright install --with-deps chromium

# Copiar todo o código da aplicação
COPY . .

# Criar diretórios de persistência para saída e logs
RUN mkdir -p /app/output /app/logs /app/Source

# Declarar volumes persistentes
VOLUME ["/app/output", "/app/logs"]

# Comando padrão: executa a pipeline principal do MRP
CMD ["python", "scripts/run_pipeline.py"]
