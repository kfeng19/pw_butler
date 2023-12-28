import pytest

from sqlalchemy.orm import Session


# Bind session to an external connection
# See https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
@pytest.fixture
def session(obtain_db):
    with obtain_db.engine.connect() as conn:
        conn.begin()
        with Session(bind=conn) as sess:
            yield sess


def test_get_salt(prepare_data, populate_db, session):
    salt = populate_db.get_salt(session, prepare_data[3])
    assert salt == prepare_data[0]


def test_get_all_sites(prepare_data, populate_db, session):
    sites = populate_db.get_all_sites(session)
    assert sites == [prepare_data[3]]
