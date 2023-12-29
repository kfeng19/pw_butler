import os
import random
import string

import pytest
from sqlalchemy import insert

from butler.database import (
    PW_KEY,
    SALT_KEY,
    SITE_KEY,
    UNAME_KEY,
    Database,
    DBCat,
    config_db,
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


def random_data(site=None):
    salt = os.urandom(16)
    pw = "".join(random.choices(string.ascii_letters, k=8)).encode()
    username = "".join(random.choices(string.ascii_letters, k=6)).encode()
    if site is None:
        site = "".join(random.choices(string.ascii_letters, k=5)).encode()
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
def prepare_data():
    return random_data(SITE_NAME)


@pytest.fixture(scope="session")
def populate_db(obtain_db, prepare_data):
    stmt = insert(obtain_db._cred_table).values(**prepare_data)
    with obtain_db.Session() as sess:
        with sess.begin():
            sess.execute(stmt)
    return obtain_db
