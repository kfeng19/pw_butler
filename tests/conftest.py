import os
import random
import string
from tempfile import TemporaryDirectory

import pytest
from sqlalchemy import insert
from sqlalchemy.orm import Session

from butler.database import PW_KEY, SALT_KEY, SITE_KEY, UNAME_KEY, Database, config_db
from butler.util import encrypt_with_salt

ROOT_PW = b"root_password"
SITE_NAME = "times"
UNAME_RAW_KEY = "uname_raw"
PW_RAW_KEY = "pw_raw"


@pytest.fixture(scope="session")
def get_db_config(docker_ip, docker_services):
    with TemporaryDirectory() as _dir:
        if config_db(
            db_name="my_db",
            host=docker_ip,
            user="db_user",
            password="mypassword",
            port=docker_services.port_for("db", 5432),
            config_dir=_dir,
        ):
            yield _dir
        else:
            raise RuntimeError("Failed to config db.")


@pytest.fixture(scope="session")
def obtain_db(get_db_config):
    db = Database(config_dir=get_db_config)
    db.reflect()
    yield db
    db.close()


def random_raw():
    pw = "".join(random.choices(string.ascii_letters, k=8))
    username = "".join(random.choices(string.ascii_letters, k=6))
    site = "".join(random.choices(string.ascii_letters, k=5))
    return site, username, pw


def random_data(site=None):
    raw_site, username, pw = random_raw()
    salt = os.urandom(16)
    if site is None:
        site = raw_site
    pw_token = encrypt_with_salt(ROOT_PW, salt, pw.encode())
    uname_token = encrypt_with_salt(ROOT_PW, salt, username.encode())
    return {
        SALT_KEY: salt,
        UNAME_KEY: uname_token.decode(),
        PW_KEY: pw_token.decode(),
        SITE_KEY: site,
        UNAME_RAW_KEY: username,
        PW_RAW_KEY: pw,
    }


def get_db_data(data: dict) -> dict:
    """Extract data only contained in database"""
    return {k: data[k] for k in [SALT_KEY, UNAME_KEY, PW_KEY, SITE_KEY]}


@pytest.fixture(scope="session")
def prepare_data():
    return random_data(SITE_NAME)


@pytest.fixture(scope="session")
def populate_db(obtain_db, prepare_data):
    stmt = insert(obtain_db._cred_table).values(**get_db_data(prepare_data))
    with obtain_db.Session() as sess:
        with sess.begin():
            sess.execute(stmt)
    return obtain_db


# Bind session to an external connection
# https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-
# session-into-an-external-transaction-such-as-for-test-suites
@pytest.fixture
def get_session(obtain_db):
    with obtain_db.engine.connect() as conn:
        conn.begin()
        with Session(bind=conn) as sess:
            yield sess
