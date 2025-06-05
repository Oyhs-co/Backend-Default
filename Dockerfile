FROM python:3.12-slim

# Instala solo lo esencial del sistema para compilar y ejecutar dependencias Python
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential libffi-dev libpq-dev libssl-dev make tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia solo los archivos de dependencias primero (mejor cacheo)
COPY pyproject.toml poetry.lock* ./

# Instala Poetry, wheel y dependencias del proyecto SIN dev
RUN pip install --no-cache-dir wheel && \
    pip install --no-cache-dir poetry==1.8.2 && \
    poetry config virtualenvs.create false && \
    poetry install --without dev --no-interaction --no-ansi && \
    pip uninstall -y poetry && \
    apt-get purge -y --auto-remove gcc build-essential make && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /root/.cache/pip /root/.cache/poetry

# Copia el resto del código
COPY ./api ./api
COPY ./sources ./sources

# Elimina archivos pyc y cachés innecesarios
RUN find /app -type d -name __pycache__ -exec rm -rf {} + && \
    find /app -type f -name '*.pyc' -delete

# Crea los __init__.py necesarios (si realmente los necesitas)
RUN find /app/api -type d -exec touch {}/__init__.py \;

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "api.api_gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]