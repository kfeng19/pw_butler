import pytest
from .conftest import ROOT_PW, SITE_NAME

from butler.app import Butler
from butler.database import DBCat


@pytest.fixture(scope="module")
def get_butler(populate_db):
    with Butler(DBCat.Test, ROOT_PW) as app:
        yield app


def test_retrieve_all(get_butler):
    all_sites = get_butler.retrieve_all()
    assert all_sites == [SITE_NAME]
