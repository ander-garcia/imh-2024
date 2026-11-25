#!/bin/sh
set -e
export QT_QPA_PLATFORM=xcb
/opt/opcua/bin/python /opt/opcua/seed_settings.py || true
exec /opt/opcua/bin/opcua-client
