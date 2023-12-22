import typing

from butler.database import DatabaseApplication, DBCat


class Butler(DatabaseApplication):
    """Main application class
    :param cat: testing or production type
    """

    def __init__(self, cat: DBCat):
        super().__init__(cat)
        self._root_pw = None

    @typing.no_type_check
    def retrieve_uname(self) -> bytes:
        pass

    @typing.no_type_check
    def retrieve_all(self) -> list:
        """Obtain all apps / sites"""
        pass
