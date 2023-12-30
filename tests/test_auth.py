import tempfile

from butler.authentication import initialize, verify_password


def test_auth(monkeypatch):
    pw = b"password"
    monkeypatch.setattr("builtins.input", lambda _: "y")
    with tempfile.NamedTemporaryFile() as auth_file:
        initialize(pw, auth_file.name)
        assert verify_password(pw, auth_file.name)
