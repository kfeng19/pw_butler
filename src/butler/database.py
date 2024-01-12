import logging
import os
import time
from abc import ABC
from configparser import ConfigParser
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Union

import pandas as pd
import sqlalchemy as sa
from sqlalchemy import Connection, MetaData, insert, select
from sqlalchemy.engine import URL, Row
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

DB_CONF_PATH = Path(os.path.expanduser("~/.pw_butler/db"))
CRED_TABLE = "credential"

HOST_KEY = "host"
DB_NAME_KEY = "db_name"
DB_USER_KEY = "user"
DB_PW_FILE = "password"
DB_PORT_KEY = "port"

SITE_KEY = "app_site"
SALT_KEY = "salt"
UNAME_KEY = "username"
PW_KEY = "password"

INI_NAME = ".ini"
INI_SECTION = "DEFAULT"


def config_db(
    password: str,
    db_name: str = "postgres",
    user: str = "postgres",
    host: str = "localhost",
    port: int = 5432,
    config_dir: str | os.PathLike = DB_CONF_PATH,
) -> bool:
    """Initialize the DB config file"""
    os.makedirs(config_dir, exist_ok=True)
    if len(os.listdir(config_dir)) > 0:
        logging.warning("Database config exists!")
        user_input = input("Overwrite? (y/n): ")
        if user_input.lower() != "y":
            logging.info("Canceled")
            return False
    config = ConfigParser()
    config[INI_SECTION] = {
        HOST_KEY: host,
        DB_PORT_KEY: str(port),
        DB_NAME_KEY: db_name,
        DB_USER_KEY: user,
    }
    _dir = Path(config_dir)
    with open(_dir / INI_NAME, "w") as f:
        config.write(f)
    os.chmod(_dir / INI_NAME, 0o640)
    with open(_dir / DB_PW_FILE, "w") as f:
        f.write(password)
    os.chmod(_dir / DB_PW_FILE, 0o640)
    return True


class DatabaseApplication(ABC):
    """Base class for anything that needs to communicate with the database"""

    def __init__(self, config_dir=DB_CONF_PATH):
        self._database = Database(config_dir)

    def __enter__(self):
        self._database.reflect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._database.close()

    @contextmanager
    def session_factory(self, session=None):
        """Return either externally provided or newly created session"""
        created = False
        if session is None:
            session = self._database.Session()
            created = True
        try:
            yield session
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if created:
                session.close()


class Database:
    """Database class
    :param config_dir: location to store database config
    """

    max_retry = 5

    def __init__(self, config_dir: str | os.PathLike = DB_CONF_PATH):
        if not os.path.isdir(config_dir):
            raise NotADirectoryError("Initialize DB config first!")
        parser = ConfigParser()
        _dir = Path(config_dir)
        parser.read(_dir / INI_NAME)
        with open(_dir / DB_PW_FILE, "r") as f:
            db_pw = f.read()
        url = URL.create(
            drivername="postgresql+psycopg",
            host=parser.get(INI_SECTION, HOST_KEY),
            port=parser.getint(INI_SECTION, DB_PORT_KEY),
            database=parser.get(INI_SECTION, DB_NAME_KEY),
            username=parser.get(INI_SECTION, DB_USER_KEY),
            password=db_pw,
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
        if hasattr(self, "engine"):
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

    def get_salt(self, conn: Union[Session, Connection], site: str) -> bytes:
        """Get the salt for a specific site token"""
        stmt = select(self._cred_table.c.salt).where(
            self._cred_table.c.app_site == site
        )
        rows = conn.execute(stmt).all()
        n = len(rows)
        if n != 1:
            raise ValueError(f"{n} rows matched when getting salt!")
        return rows[0][0]

    def get_all_sites(self, conn: Union[Session, Connection]) -> list:
        """Obtain all site tokens in database"""
        stmt = select(self._cred_table.c.app_site)
        return list(conn.scalars(stmt).all())

    def get_uname(self, sess: Session, site: str) -> pd.DataFrame:
        """Obtain username for site"""
        query = select(self._cred_table.c.username, self._cred_table.c.salt).where(
            site == self._cred_table.c.app_site
        )
        return pd.read_sql(query, sess.get_bind())

    def get_pw(
        self, sess: Union[Session, Connection], site: str, uname_token: str
    ) -> Row:
        """Obtain password for site and username"""
        query = (
            select(self._cred_table.c.password, self._cred_table.c.salt)
            .where(site == self._cred_table.c.app_site)
            .where(uname_token == self._cred_table.c.username)
        )
        return sess.execute(query).one()

    def add(self, conn: Union[Session, Connection], entry: dict):
        """Add one entry"""
        query = (
            select(self._cred_table)
            .where(entry[SITE_KEY] == self._cred_table.c.app_site)
            .where(entry[UNAME_KEY] == self._cred_table.c.username)
        )
        if len(conn.execute(query).all()):
            raise ValueError("Entry already exists!")
        stmt = insert(self._cred_table).values(**entry)
        conn.execute(stmt)
        conn.commit()
