set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER"  <<-EOSQL         
    CREATE DATABASE grafana;
    CREATE USER grafanauser WITH ENCRYPTED PASSWORD 'grafanaPass2022';
    GRANT ALL PRIVILEGES ON DATABASE grafana TO grafanauser;
    -- PostgreSQL 15+ no longer lets non-owners create objects in schema public;
    -- making grafanauser the owner lets Grafana create its tables.
    ALTER DATABASE grafana OWNER TO grafanauser;
EOSQL