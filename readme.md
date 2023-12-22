Password Butler
===
A password manager on local host.

Usage
---
The first step is to have the database ready.
The easiest way to achieve this is through docker-compose:
```commandline
docker-compose up
```
This will create a persistent database.
When you are done with the tool, simply stop everything with
```
docker-compose down
```

Alternatively, you may build a custom image with the Dockerfile and start the database container manually:
```commandline
docker run -d --name db_server \
    -e POSTGRES_DB=pw_db
    -e POSTGRES_PASSWORD=mysecretpassword \
    -v pw_vol:/var/lib/postgresql/data \
    pw_image
```
Here `pw_image` is the name of the image built with our Dockerfile.

As long as the same volume is used, database initialization will be skipped for new containers.

References
---
Acknowledgement for the following inspiring works:
1. [felipewom/docker-compose-postgres](https://github.com/felipewom/docker-compose-postgres)
2. [alexandre-lavoie/python-sql-password-manager](https://github.com/alexandre-lavoie/python-sql-password-manager)
3. [collinsmc23/python-sql-password-manager](https://github.com/collinsmc23/python-sql-password-manager)
