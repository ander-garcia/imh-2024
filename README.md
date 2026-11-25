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

Python examples (`python/`) require Python >= 3.12: `pip install -r python/requirements.txt`.

MQTT web client: open http://localhost:8086 (MQTTX Web). Click "New Connection": it is prefilled with
`ws://<host>:9002/mqtt` and user `imh-client`; enter the password and connect. The broker's WebSocket
listener (container port 9001) is published on host port 9002.

OPC UA explorer (UaExpert-like, FreeOpcUa opcua-client): open http://localhost:5800. The address box is preset to
`opc.tcp://opc-micro:50000`; click Connect, keep Security "None" / Anonymous and click Connect again. Browse the tree,
right-click a variable to subscribe or plot it. The image is built locally from `opcua-client/`
(first `docker compose up` builds it; rebuild with `docker compose build opcua-client`).
