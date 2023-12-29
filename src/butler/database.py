import enum
import os.path
import time
from abc import ABC
from configparser import ConfigParser
from typing import Any, Union

import sqlalchemy as sa
from sqlalchemy import MetaData, select, Connection, insert
from sqlalchemy.engine import URL
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, Session

DB_CONF_PATH = os.path.expanduser("~/.pw_butler/db.ini")
CRED_TABLE = "credential"

HOST_KEY = "host"
DB_NAME_KEY = "db_name"
DB_USER_KEY = "user"
DB_PW_KEY = "password"
DB_PORT_KEY = "port"

SITE_KEY = "app_site"
SALT_KEY = "salt"
UNAME_KEY = "username"
PW_KEY = "password"


class DBCat(enum.Enum):
    Test = 1
    Prod = 2


def config_db(
    mode: DBCat, host: str, db_name: str, user: str, password: str, port=5432
) -> None:
    """Initialize the DB config file"""
    config = ConfigParser()
    if os.path.isfile(DB_CONF_PATH):
        config.read(DB_CONF_PATH)
    config[mode.name] = {
        HOST_KEY: host,
        DB_NAME_KEY: db_name,
        DB_USER_KEY: user,
        DB_PW_KEY: password,
        DB_PORT_KEY: port,
    }
    with open(DB_CONF_PATH, "w") as f:
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
            raise FileNotFoundError("Initialize DB config first!")
        parser = ConfigParser()
        parser.read(DB_CONF_PATH)
        url = URL.create(
            drivername="postgresql+psycopg",
            host=parser.get(category.name, HOST_KEY),
            database=parser.get(category.name, DB_NAME_KEY),
            username=parser.get(category.name, DB_USER_KEY),
            password=parser.get(category.name, DB_PW_KEY),
            port=parser.getint(category.name, DB_PORT_KEY),
        )
        self.engine = sa.create_engine(url)  # An engine for connection
        self.Session = sessionmaker(
            self.engine
        )  # A convenience session factory for production (NOT for testing)
        self._cred_table: Any = None  # Placeholder for our credential table

    def close(self):
        """Close connections"""
        self.engine.dispose()

    def __del__(self):
        """Destructor"""
        self.close()

    def reflect(self) -> None:
        """Reflect tables from our database"""
        meta = MetaData()
        for k in range(self.max_retry):
            try:
                meta.reflect(bind=self.engine)
            except OperationalError as e:
                if k == self.max_retry - 1:
                    raise e
                print("Reflecting failed. Database may not be ready yet. Retrying...")
                time.sleep(1)
        if CRED_TABLE not in meta.tables:
            raise KeyError(f"Didn't find {CRED_TABLE} in database!")
        self._cred_table = meta.tables[CRED_TABLE]

    def get_salt(self, conn: Union[Session, Connection], site_token: str) -> bytes:
        """Get the salt for a specific site token"""
        stmt = select(self._cred_table.c.salt).where(
            self._cred_table.c.app_site == site_token
        )
        rows = conn.execute(stmt).all()
        n = len(rows)
        if n != 1:
            raise ValueError(f"{n} rows matched when getting salt!")
        return rows[0][0]

    def get_all_sites(self, conn: Union[Session, Connection]) -> list:
        """Obtain all site tokens in database"""
        stmt = select(self._cred_table.c.app_site)
        rows = conn.execute(stmt).all()
        return [row[0] for row in rows]

    def add(self, conn: Union[Session, Connection], entry: dict):
        """Add one entry"""
        query = (
            select(self._cred_table)
            .where(entry[SITE_KEY] == self._cred_table.c.app_site)
            .where(entry[UNAME_KEY] == self._cred_table.c.username)
            .where(entry[PW_KEY] == self._cred_table.c.password)
        )
        if len(conn.execute(query).all()):
            raise ValueError("Entry already exists!")
        stmt = insert(self._cred_table).values(**entry)
        conn.execute(stmt)
        conn.commit()
