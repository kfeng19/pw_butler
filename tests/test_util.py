from butler.util import derive_key, encrypt_with_salt, decrypt_with_salt, encrypt_wrapper

salt = b'\x95\xfdi\x83\x1e\xb8\x04T'
pw = b'lol'
secret = b'secret'


def test_derive_key():
    expected = b'Xvj8lEOELtCcXGUvS0kTGN9jcnt5Z80X2aOzyhdK8r8='
    assert expected == derive_key(salt, pw)


def test_encrypt_decrypt():
    token = encrypt_with_salt(pw, salt, secret)
    new_secret = decrypt_with_salt(pw, salt, token)
    assert new_secret == secret


def test_encrypt_wrapper():
    token, my_salt = encrypt_wrapper(pw, secret)
    new_secret = decrypt_with_salt(pw, my_salt, token)
    assert new_secret == secret