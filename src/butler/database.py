import enum
import os.path
from configparser import ConfigParser
from abc import ABC
import time

import sqlalchemy as sa
from sqlalchemy import MetaData
from sqlalchemy.engine import URL
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

DB_CONF_PATH = os.path.expanduser('~/.pw_butler/db.ini')
CRED_TABLE = "credential"

HOST_KEY = "host"
DB_NAME_KEY = "db_name"
DB_USER_KEY = "user"
DB_PW_KEY = "password"
DB_PORT_KEY = "port"


class DBCat(enum.Enum):
    Test = 1
    Prod = 2


def config_db(mode: DBCat, host: str, db_name: str, user: str, password: str, port=5432) -> None:
    """Initialize the DB config file"""
    config = ConfigParser()
    if os.path.isfile(DB_CONF_PATH):
        config.read(DB_CONF_PATH)
    config[mode.name] = {
        HOST_KEY: host,
        DB_NAME_KEY: db_name,
        DB_USER_KEY: user,
        DB_PW_KEY: password,
        DB_PORT_KEY: port
    }
    with open(DB_CONF_PATH, 'w') as f:
        config.write(f)


class DatabaseApplication(ABC):
    """Base class for anything that needs to communicate with the database"""
    def __init__(self, category: DBCat):
        self._database = Database(category)

    def __enter__(self):
        self._database.reflect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._database.close()


class Database:
    """Database class
    :param category: whether this instance is for production or testing
    """
    max_retry = 5

    def __init__(self, category: DBCat):
        if not os.path.isfile(DB_CONF_PATH):
            raise FileNotFoundError(f"Initialize DB config first!")
        parser = ConfigParser()
        parser.read(DB_CONF_PATH)
        url = URL.create(
            drivername="postgresql+psycopg",
            host=parser.get(category.name, HOST_KEY),
            database=parser.get(category.name, DB_NAME_KEY),
            username=parser.get(category.name, DB_USER_KEY),
            password=parser.get(category.name, DB_PW_KEY),
            port=parser.getint(category.name, DB_PORT_KEY)
        )
        self._engine = sa.create_engine(url)  # An engine for connection
        self.Session = sessionmaker(self._engine)  # A convenience session factory for production (NOT for testing)
        self._cred_table = None  # Placeholder for our credential table

    def close(self):
        """Close connections"""
        self._engine.dispose()

    def __del__(self):
        """Destructor"""
        self.close()

    def reflect(self) -> None:
        """Reflect tables from our database"""
        meta = MetaData()
        for k in range(self.max_retry):
            try:
                meta.reflect(bind=self._engine)
            except OperationalError as e:
                if k == self.max_retry - 1:
                    raise e
                print("Reflecting failed. Database may not be ready yet. Retrying...")
                time.sleep(1)
        if CRED_TABLE not in meta.tables:
            raise KeyError(f"Didn't find {CRED_TABLE} in database!")
        self._cred_table = meta.tables[CRED_TABLE]

    def get_salt(self) -> bytes:
        pass
