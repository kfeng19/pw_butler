import pandas as pd
from pytest import raises

from butler.database import PW_KEY, SALT_KEY, SITE_KEY, UNAME_KEY

from .conftest import SITE_NAME, random_data


def test_get_salt(prepare_data, populate_db, get_session):
    salt = populate_db.get_salt(get_session, prepare_data[SITE_KEY])
    assert salt == prepare_data[SALT_KEY]


def test_get_all_sites(prepare_data, populate_db, get_session):
    sites = populate_db.get_all_sites(get_session)
    assert sites == [prepare_data[SITE_KEY]]


def test_get_uname(prepare_data, populate_db, get_session):
    expected = pd.DataFrame.from_dict(
        {
            UNAME_KEY: [prepare_data[UNAME_KEY]],
            SALT_KEY: [prepare_data[SALT_KEY]],
        }
    )
    uname = populate_db.get_uname(get_session, prepare_data[SITE_KEY])
    assert expected.equals(uname)


def test_get_pw(prepare_data, populate_db, get_session):
    expected_token = prepare_data[PW_KEY]
    expected_salt = prepare_data[SALT_KEY]
    result = populate_db.get_pw(get_session, SITE_NAME, prepare_data[UNAME_KEY])
    assert expected_salt == getattr(result, SALT_KEY)
    assert expected_token == getattr(result, PW_KEY)


def test_add_duplicate(prepare_data, populate_db, get_session):
    with raises(ValueError, match="exists"):
        populate_db.add(get_session, prepare_data)


def test_add(populate_db, get_session):
    data = random_data()
    populate_db.add(get_session, data)
    salt = populate_db.get_salt(get_session, data[SITE_KEY])
    assert salt == data[SALT_KEY]
