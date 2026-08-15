FROM odoo:19.0

USER root

# Limpiamos posibles metadatos corruptos y actualizamos
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Instalamos la librería 'culqi' (este es el nombre correcto del paquete en PyPI)
# Usamos --no-cache-dir para una instalación limpia
RUN pip3 install --break-system-packages --no-cache-dir culqi

USER odoo