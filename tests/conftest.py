import os

import pytest
from sqlalchemy import insert

from butler.database import config_db, DBCat, Database
from butler.util import encrypt_with_salt

ROOT_PW = b"root_password"


@pytest.fixture(scope="session")
def config(docker_ip, docker_services):
    config_db(
        DBCat.Test,
        docker_ip,
        "my_db",
        "db_user",
        "mypassword",
        docker_services.port_for("db", 5432),
    )


@pytest.fixture(scope="session")
def obtain_db(config):
    db = Database(DBCat.Test)
    db.reflect()
    yield db
    db.close()


@pytest.fixture(scope="session")
def prepare_data():
    salt = os.urandom(16)
    pw = b"user_password"
    username = b"user_name"
    pw_token = encrypt_with_salt(ROOT_PW, salt, pw)
    uname_token = encrypt_with_salt(ROOT_PW, salt, username)
    return salt, uname_token, pw_token


@pytest.fixture(scope="session")
def populate_db(obtain_db, prepare_data):
    stmt = insert(obtain_db._cred_table).values(
        app_site="Times",
        salt=prepare_data[0],
        username=prepare_data[1],
        password=prepare_data[2],
    )
    with obtain_db.Session() as sess:
        with sess.begin():
            sess.execute(stmt)
