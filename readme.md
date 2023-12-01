Password Butler
===
A password manager on local host.

Usage
---
As the first step, please start the database container using a command such as
```commandline
docker run -d --name db_server \
    -e POSTGRES_DB=pw_db
    -e POSTGRES_PASSWORD=mysecretpassword \
    -v pw_vol:/var/lib/postgresql/data \
    pw_image
```
Here `pw_image` is the name of the image built with our Dockerfile. 

One may keep using the same container afterward. 
But if a new container needs to be spun up, with the same volume, 
all the environment variables are no longer relevant as they seem to be overwritten by the existing database in the volume.