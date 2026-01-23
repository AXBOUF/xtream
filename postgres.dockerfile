# ============================================================================
# POSTGRESQL DATABASE DOCKERFILE
# ============================================================================
FROM postgres:15-alpine

ENV POSTGRES_DB=washdata_db
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres

# Copy schema initialization script
COPY project0/dataschema/dailyreport.sql /docker-entrypoint-initdb.d/01-schema.sql

EXPOSE 5432
