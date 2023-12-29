import os

import pytest
from sqlalchemy import insert

from butler.database import (
    config_db,
    DBCat,
    Database,
    SALT_KEY,
    UNAME_KEY,
    SITE_KEY,
    PW_KEY,
)
from butler.util import encrypt_with_salt

ROOT_PW = b"root_password"
SITE_NAME = b"times"


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
    site = SITE_NAME
    pw_token = encrypt_with_salt(ROOT_PW, salt, pw)
    uname_token = encrypt_with_salt(ROOT_PW, salt, username)
    site_token = encrypt_with_salt(ROOT_PW, salt, site)
    return {
        SALT_KEY: salt,
        UNAME_KEY: uname_token.decode(),
        PW_KEY: pw_token.decode(),
        SITE_KEY: site_token.decode(),
    }


@pytest.fixture(scope="session")
def populate_db(obtain_db, prepare_data):
    stmt = insert(obtain_db._cred_table).values(**prepare_data)
    with obtain_db.Session() as sess:
        with sess.begin():
            sess.execute(stmt)
    return obtain_db
