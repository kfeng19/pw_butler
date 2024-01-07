import logging

from butler.database import (
    DB_CONF_PATH,
    PW_KEY,
    SALT_KEY,
    SITE_KEY,
    UNAME_KEY,
    DatabaseApplication,
)
from butler.util import decrypt_with_salt, encrypt_with_salt, encrypt_wrapper


class Butler(DatabaseApplication):
    """Main application class
    :param password: root password
    :param db_dir: testing or production type
    """

    def __init__(self, password, db_dir=DB_CONF_PATH):
        super().__init__(db_dir)
        self._root_pw = password

    def retrieve_uname(self, site_name: str) -> list:
        """Obtain usernames for a site / app"""
        with self.session_factory() as sess:
            tokens = self._database.get_uname(sess, site_name)
        unames = []
        for i in tokens.index:
            unames.append(
                decrypt_with_salt(
                    self._root_pw, tokens[SALT_KEY][i], tokens[UNAME_KEY][i]
                ).decode()
            )
        return unames

    def retrieve_all(self) -> list:
        """Obtain all apps / sites"""
        with self.session_factory() as sess:
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
