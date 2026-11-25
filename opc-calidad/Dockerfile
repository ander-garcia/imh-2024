# Simulador OPC UA de una estación de control de calidad por visión
# (imagen PNG, cota, resultado OK/NOT OK y contador). Endpoint: opc.tcp://<host>:4840/calidad
FROM python:3.14-slim

RUN pip install --no-cache-dir asyncua==2.1.0 pillow==13.0.0

WORKDIR /app
COPY servidor_opcua_calidad.py .

# Sin buffer, para que "docker logs" muestre cada pieza al momento
ENV PYTHONUNBUFFERED=1 \
    PERIODO=2

EXPOSE 4840
CMD ["sh", "-c", "exec python servidor_opcua_calidad.py --periodo ${PERIODO} --puerto 4840"]
