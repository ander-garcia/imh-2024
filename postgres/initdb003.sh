set -e
# Resultados de la estación de control de calidad (servicio opc-calidad),
# guardados por el flujo de Node-RED opc-calidad/flujo_nodered_calidad.json.
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE TABLE IF NOT EXISTS public.calidad
    (
        "time"      timestamp with time zone NOT NULL,
        pieza       integer NOT NULL,          -- Contador de la estación
        cota_mm     double precision,          -- Cota medida (mm)
        resultado   smallint,                  -- 1 = OK, 0 = NOT OK
        imagen      bytea                      -- Imagen PNG de la pieza
    );
    -- 1-hour chunks so the retention policy can drop old data in small steps
    SELECT create_hypertable('calidad', by_range('time', INTERVAL '1 hour'), if_not_exists => TRUE);
    SELECT set_chunk_time_interval('calidad', INTERVAL '1 hour');
    -- Keep only the last day (~400 MB at one piece every 2 s, mostly images)
    SELECT add_retention_policy('calidad', INTERVAL '1 day', if_not_exists => TRUE);
    -- Run the cleanup every hour (default is once a day, which could leave up to 2 days)
    SELECT alter_job(job_id, schedule_interval => INTERVAL '1 hour')
      FROM timescaledb_information.jobs
     WHERE proc_name = 'policy_retention' AND hypertable_name = 'calidad';
    GRANT SELECT ON TABLE public.calidad TO grafanareader;
EOSQL
