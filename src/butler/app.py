import logging
import typing

from butler.database import (
    DB_CONF_PATH,
    PW_KEY,
    SALT_KEY,
    SITE_KEY,
    UNAME_KEY,
    DatabaseApplication,
)
from butler.util import encrypt_with_salt, encrypt_wrapper


class Butler(DatabaseApplication):
    """Main application class
    :param db_dir: testing or production type
    """

    def __init__(self, password, db_dir=DB_CONF_PATH):
        super().__init__(db_dir)
        self._root_pw = password

    @typing.no_type_check
    def retrieve_uname(self) -> bytes:
        pass

    def retrieve_all(self) -> list:
        """Obtain all apps / sites"""
        with self._database.Session() as sess:
            sites = self._database.get_all_sites(sess)
        return sites

    def add(self, site_name: str, username: str, password: str, session=None) -> None:
        """Add one entry"""
        uname_token, salt = encrypt_wrapper(self._root_pw, username.encode())
        pw_token = encrypt_with_salt(self._root_pw, salt, password.encode())
        with self.session_factory(session) as sess:
            self._database.add(
                sess,
                {
                    SITE_KEY: site_name,
                    SALT_KEY: salt,
                    UNAME_KEY: uname_token.decode(),
                    PW_KEY: pw_token.decode(),
                },
            )
        logging.info("Entry added.")
