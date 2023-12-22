from butler.authentication import initialize, authenticate
import tempfile


def test_auth():
    pw = b'password'
    with tempfile.NamedTemporaryFile() as auth_file:
        initialize(pw, auth_file.name)
        assert authenticate(pw, auth_file.name)
