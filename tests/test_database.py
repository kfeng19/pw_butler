import pytest
from pytest import raises
from sqlalchemy.orm import Session

from butler.database import SALT_KEY, SITE_KEY

from .conftest import random_data


# Bind session to an external connection
# See https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
@pytest.fixture
def session(obtain_db):
    with obtain_db.engine.connect() as conn:
        conn.begin()
        with Session(bind=conn) as sess:
            yield sess


def test_get_salt(prepare_data, populate_db, session):
    salt = populate_db.get_salt(session, prepare_data[SITE_KEY])
    assert salt == prepare_data[SALT_KEY]


def test_get_all_sites(prepare_data, populate_db, session):
    sites = populate_db.get_all_sites(session)
    assert sites == [prepare_data[SITE_KEY]]


def test_add_duplicate(prepare_data, populate_db, session):
    with raises(ValueError, match="exists"):
        populate_db.add(session, prepare_data)


def test_add(populate_db, session):
    data = random_data()
    populate_db.add(session, data)
    salt = populate_db.get_salt(session, data[SITE_KEY])
    assert salt == data[SALT_KEY]
