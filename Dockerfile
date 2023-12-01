FROM postgres
COPY pw.sql /docker-entrypoint-initdb.d/
# DB credentials are specified when container is started