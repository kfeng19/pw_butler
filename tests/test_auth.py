from butler.authentication import initialize, authenticate
import tempfile


def test_auth(monkeypatch):
    pw = b'password'
    monkeypatch.setattr("builtins.input", lambda _: "y")
    with tempfile.NamedTemporaryFile() as auth_file:
        initialize(pw, auth_file.name)
        assert authenticate(pw, auth_file.name)
