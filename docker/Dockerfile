# Dockerfile para Tabula Cloud Sync Service
FROM python:3.9-slim

# Metadatos
LABEL maintainer="tu-email@empresa.com"
LABEL description="Tabula Cloud Sync Service"
LABEL version="2.0.0"

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV CONFIG_FILE=/etc/tabula/config.ini

# Crear usuario no privilegiado
RUN groupadd -r tabula && useradd -r -g tabula tabula

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .
COPY setup.py .
COPY README.md .
COPY MANIFEST.in .

# Instalar dependencias Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY core/ ./core/
COPY models/ ./models/
COPY utils/ ./utils/
COPY service/ ./service/
COPY __main__.py .
COPY config.ini.template .

# Instalar el paquete
RUN pip install --no-cache-dir -e .

# Crear directorios necesarios
RUN mkdir -p /etc/tabula /var/log/tabula && \
    chown -R tabula:tabula /etc/tabula /var/log/tabula /app

# Copiar script de entrada
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Cambiar a usuario no privilegiado
USER tabula

# Exponer puerto para health checks (opcional)
EXPOSE 8080

# Volúmenes para configuración y logs
VOLUME ["/etc/tabula", "/var/log/tabula"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "
import sys; 
sys.path.insert(0, '/app'); 
from service.base_service import TabulaCloudService; 
service = TabulaCloudService('${CONFIG_FILE}'); 
exit(0 if service.health_check() else 1)
" || exit 1

# Punto de entrada
ENTRYPOINT ["/entrypoint.sh"]
CMD ["--foreground"]
