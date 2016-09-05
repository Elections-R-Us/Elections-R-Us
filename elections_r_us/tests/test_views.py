from __future__ import unicode_literals
import pytest


VALID_LOGINS = [
    ('username', 'password'),
    ('user_name', 'eoae8uadh%$  '),
    ('User_name764', 'adiug98'),
    ('0234867', '8419tagsh')
]


BAD_USERNAMES = [
    '',
    'user name',
    '~!username',
    "robert'); DROP TABLE Students; --"
]


@pytest.mark.parametrize('username, password', VALID_LOGINS)
def test_valid_registration(username, password):
    from ..views.default import verify_registration
    assert verify_registration(username, password, password)


@pytest.mark.parametrize('username', BAD_USERNAMES)
def test_bad_username(username):
    from ..views.default import verify_registration, BadUsername
    password = 'hello'
    with pytest.raises(BadUsername):
        verify_registration(username, password, password)
