from database import DatabaseApplication, DBCat


class Butler(DatabaseApplication):
    """Main application class
    :param cat: testing or production type
    """
    def __init__(self, cat: DBCat):
        super(DatabaseApplication, self).__init__(cat)

    def retrieve_uname(self, pw: bytes) -> bytes:
        pass
