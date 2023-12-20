import base64
import time

import pytest
from butler.database import config_db, DBCat, Database
from sqlalchemy import insert
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ROOT_PW = b"root_password"


@pytest.fixture(scope="session", autouse=True)
def config(docker_ip, docker_services):
    config_db(
        DBCat.Test,
        docker_ip,
        "my_db",
        "db_user",
        "mypassword",
        docker_services.port_for("db", 5432)
    )


@pytest.fixture(scope="session")
def obtain_db(config):
    db = Database(DBCat.Test)
    for k in range(5):
        if k == 5:
            raise RuntimeError("Couldn't connect to database within max retries.")
        if db.reflect():
            break
        else:
            time.sleep(1)
    yield db
    db.close()


# Ref: https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet
@pytest.fixture(scope="module")
def prepare_data():
    salt = os.urandom(16)
    pw = b"user_password"
    username = b"user_name"

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000)

    key = base64.urlsafe_b64encode(kdf.derive(ROOT_PW))
    f = Fernet(key)
    pw_token = f.encrypt(pw)
    uname_token = f.encrypt(username)
    return salt, uname_token, pw_token


@pytest.fixture(scope="session")
def populate_db(obtain_db, prepare_data):
    stmt = (
        insert(obtain_db._cred_table).
        values(
            app_site="Times",
            salt=prepare_data[0],
            username=prepare_data[1],
            password=prepare_data[2]
        )
    )
    with obtain_db.Session() as sess:
        with sess.begin():
            sess.execute(stmt)
