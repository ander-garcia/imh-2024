# OPC UA explorer (UaExpert-like) in the browser:
# FreeOpcUa "opcua-client" (PyQt6 + asyncua, needs Python >= 3.14 -> Ubuntu 26.04) on a GUI base image that serves
# the desktop app through a web page (noVNC) on port 5800.
FROM jlesage/baseimage-gui:ubuntu-26.04-v4.15.0

# System libraries needed by the PyQt6 wheels (Qt xcb platform plugin, OpenGL, fonts)
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 python3-venv \
        libgl1 libegl1 libglib2.0-0t64 libdbus-1-3 libfontconfig1 fonts-dejavu-core \
        libxkbcommon0 libxkbcommon-x11-0 libxcb-cursor0 libxcb-icccm4 libxcb-image0 \
        libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxcb-xinerama0 \
        libxcb-xkb1 libxcb-xfixes0 libxcb-sync1 libxcb-shm0 libxrender1 libsm6 libice6 \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/opcua \
    && /opt/opcua/bin/pip install --no-cache-dir \
        opcua-client==1.0.2 \
        asyncua==2.1.0 \
        PyQt6==6.12.1 \
        pyqtgraph==0.14.0

COPY startapp.sh /startapp.sh
COPY seed_settings.py /opt/opcua/seed_settings.py
RUN chmod +x /startapp.sh \
    && set-cont-env APP_NAME "OPC UA Client" \
    && set-cont-env APP_VERSION "1.0.2"

# Default server offered in the address box (overridable from docker-compose)
ENV OPCUA_DEFAULT_ENDPOINT=opc.tcp://opc-micro:50000
