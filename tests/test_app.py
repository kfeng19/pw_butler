import pytest
from sqlalchemy import select

from butler.app import Butler
from butler.database import DBCat

from .conftest import ROOT_PW, SITE_NAME, random_raw


@pytest.fixture(scope="module")
def get_butler(populate_db):
    with Butler(DBCat.Test, ROOT_PW) as app:
        yield app


def test_retrieve_all(get_butler, prepare_data):
    all_sites = get_butler.retrieve_all()
    assert all_sites == [SITE_NAME]


def test_add(get_butler, get_session, populate_db):
    site, uname, pw = random_raw()
    get_butler.add(site, uname, pw, get_session)
    table = populate_db._cred_table
    stmt = select(table).where(table.c.app_site == site)
    rows = get_session.execute(stmt).all()
    assert len(rows) == 1
