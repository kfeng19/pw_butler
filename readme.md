Password Butler
===
A password manager on local host.

Dependencies
---
Password Butler (referred to as Butler below) depends on Docker for database hosting,
so please install Docker before using it.

Butler supports Python 3.10 and up.

Installation
---
You can install Butler like any other Python packages.
Create a fresh virtual environment using your favorite tool such as Conda or venv.
Install Butler with:
```commandline
pip install .
```

Usage
---
Butler has a simple command line interface. Simply type
```commandline
butler
```
And you will get a list of available commands.
For first time use, you want to start with
```commandline
butler init
```
And the CLI will guide you through setting up your root password and configuring
the database.

Every time before using Butler, you have to first fire up the backend service with
```commandline
butler up
```
Then you may use any available commands such as `butler add` and `butler get`.
When you are done, please remember to issue
```commandline
butler down
```
to shut down the backend service.

References
---
Acknowledgement for the following inspiring works:
1. [felipewom/docker-compose-postgres](https://github.com/felipewom/docker-compose-postgres)
2. [alexandre-lavoie/python-sql-password-manager](https://github.com/alexandre-lavoie/python-sql-password-manager)
3. [collinsmc23/python-sql-password-manager](https://github.com/collinsmc23/python-sql-password-manager)
