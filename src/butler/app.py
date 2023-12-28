import typing

from butler.database import DatabaseApplication, DBCat

from butler.util import decrypt_with_salt


class Butler(DatabaseApplication):
    """Main application class
    :param cat: testing or production type
    """

    def __init__(self, cat: DBCat, password):
        super().__init__(cat)
        self._root_pw = password

    @typing.no_type_check
    def retrieve_uname(self) -> bytes:
        pass

    def retrieve_all(self) -> list:
        """Obtain all apps / sites"""
        sites = []
        with self._database.Session() as sess:
            tokens = self._database.get_all_sites(sess)
            for token in tokens:
                salt = self._database.get_salt(sess, token)
                sites.append(decrypt_with_salt(self._root_pw, salt, token))
        return sites
