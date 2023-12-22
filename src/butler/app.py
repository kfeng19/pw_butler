from database import DatabaseApplication, DBCat


class Butler(DatabaseApplication):
    """Main application class
    :param cat: testing or production type
    """
    def __init__(self, cat: DBCat):
        super(DatabaseApplication, self).__init__(cat)
        self._root_pw = None

    def retrieve_uname(self) -> bytes:
        pass

    def retrieve_all(self) -> list:
        """Obtain all apps / sites"""
        pass
