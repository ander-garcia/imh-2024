Deploy using docker compose

```
docker compose up -d
```

First run / after upgrading:

- Node-RED contrib nodes are not committed (`node-red-data/node_modules` is ignored). Install them once, then restart Node-RED:

  ```
  docker compose exec node-red sh -c "cd /data && npm install"
  docker compose restart node-red
  ```

- TimescaleDB runs on PostgreSQL 18 and uses a new volume (`timescale-data-pg18`, mounted at `/var/lib/postgresql`).
  The old `timescale-data` (PostgreSQL 14) volume is not reused; the init scripts recreate the schema on first start.
  Export any data you need from the old volume with `pg_dump` before removing it.

Grafana: open http://localhost:3000 (admin / `GF_SECURITY_ADMIN_PASSWORD`). The home page is the "Control de calidad"
dashboard; "Caldera" is linked from it. Both are provisioned from `grafana/dashboards/` (folder "IMH", read-only in
the UI: edit the JSON files, Grafana reloads them within 30 s). The latest-piece image uses the Business Text panel
plugin, installed at startup (`GF_PLUGINS_PREINSTALL_SYNC`, needs Internet on first start).

Python examples (`python/`) require Python >= 3.12: `pip install -r python/requirements.txt`.

MQTT web client: open http://localhost:8086 (MQTTX Web). Click "New Connection": it is prefilled with
`ws://<host>:9002/mqtt` and user `imh-client`; enter the password and connect. The broker's WebSocket
listener (container port 9001) is published on host port 9002.

OPC UA explorer (UaExpert-like, FreeOpcUa opcua-client): open http://localhost:5800. The address box is preset to
`opc.tcp://opc-micro:50000`; click Connect, keep Security "None" / Anonymous and click Connect again. Browse the tree,
right-click a variable to subscribe or plot it. The image is built locally from `opcua-client/`
(first `docker compose up` builds it; rebuild with `docker compose build opcua-client`).

Quality-control simulator (`opc-calidad`, built from `opc-calidad/`): an OPC UA server that simulates a vision
inspection station. Every `PERIODO` seconds (default 2) it publishes, under the `ControlCalidad` object:
`ns=2;s=Imagen` (PNG, ByteString), `ns=2;s=Cota_mm` (Double, nominal 25.00 ± 0.10 mm),
`ns=2;s=Resultado` (Int16, 1 = OK, 0 = NOT OK) and `ns=2;s=Contador` (UInt32).
Endpoint: `opc.tcp://opc-calidad:4840/calidad` from other containers (Node-RED, OPC UA explorer), or
`opc.tcp://localhost:4840/calidad` from the host. `opc-calidad/flujo_nodered_calidad.json` is a Node-RED flow
(import it in Node-RED; uses the already installed `node-red-contrib-opcua`, `@flowfuse/node-red-dashboard` and
`node-red-contrib-postgresql`) that:
- shows the image, OK / NOT OK, gauge, counter and history chart on the Dashboard 2 page
  http://localhost:1880/dashboard/calidad;
- stores every inspected piece in the TimescaleDB table `in4pl.calidad` (`time`, `pieza`, `cota_mm`, `resultado`,
  `imagen` as PNG `bytea`), created by `postgres/initdb003.sh`. The DB user/password come from the
  `CALIDAD_DB_USER` / `CALIDAD_DB_PASSWORD` variables of the `node-red` service. About 10 kB per piece
  (~400 MB/day at the default 2 s period); a TimescaleDB retention policy keeps only the last day.
