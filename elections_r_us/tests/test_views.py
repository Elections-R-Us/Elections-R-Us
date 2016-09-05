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

BAD_PASSWORDS = [
    '',
    'fjvi',
    'V%@35',
]

UNMATCHED_PASSWORDS = [
    ('654616565', '654982330'),
    ('986asdga', '56464asgassg'),
    ('asgasdh0', 'ahdfharth')
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


@pytest.mark.parametrize('password', BAD_PASSWORDS)
def test_bad_password(password):
    from ..views.default import verify_registration, BadPassword
    username = 'username'
    with pytest.raises(BadPassword):
        verify_registration(username, password, password)


@pytest.mark.parametrize('p1, p2', UNMATCHED_PASSWORDS)
def test_unmatched_password(p1, p2):
    from ..views.default import verify_registration, UnmatchedPassword
    username = 'username'
    with pytest.raises(UnmatchedPassword):
        verify_registration(username, p1, p2)
