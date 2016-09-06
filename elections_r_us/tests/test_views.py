from __future__ import unicode_literals
import pytest
from pyramid.httpexceptions import HTTPFound
from pyramid import testing


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


def test_existent_user(session_with_user):
    from ..views.default import user_exists
    session, username, password = session_with_user
    assert user_exists(session, username)


def test_nonexistent_user(new_session):
    from ..views.default import user_exists
    username = 'username'
    assert not user_exists(new_session, username)


def dummy_post_request(new_session, params):
    dummy = testing.DummyRequest(post=params)
    dummy.dbsession = new_session
    return dummy


def test_login_view_success(session_with_user):
    from ..views.default import login_view
    session, username, password = session_with_user
    login_results = login_view(dummy_post_request(session, {
        'username': username,
        'password': password
    }))
    assert isinstance(login_results, HTTPFound)


def test_login_view_failure(new_session):
    from ..views.default import login_view
    login_results = login_view(dummy_post_request(new_session, {
        'username': 'username',
        'password': 'password'
    }))
    assert login_results == {'login_failure': True}


@pytest.mark.parametrize('username, password', VALID_LOGINS)
def test_register_view_success(new_session, username, password):
    from ..views.default import register_view
    register_results = register_view(dummy_post_request(new_session, {
        'username': username,
        'password': password,
        'password_confirm': password
    }))
    assert isinstance(register_results, HTTPFound)


@pytest.mark.parametrize('username', BAD_USERNAMES)
def test_register_view_bad_username(new_session, username):
    from ..views.default import register_view
    register_results = register_view(dummy_post_request(new_session, {
        'username': username,
        'password': 'password',
        'password_confirm': 'password'
    }))
    assert register_results == {'bad_username': True}


@pytest.mark.parametrize('password', BAD_PASSWORDS)
def test_register_view_bad_password(new_session, password):
    from ..views.default import register_view
    register_results = register_view(dummy_post_request(new_session, {
        'username': 'username',
        'password': password,
        'password_confirm': password
    }))
    assert register_results == {'bad_password': True}


@pytest.mark.parametrize('p1, p2', UNMATCHED_PASSWORDS)
def test_register_view_unmatched_passwords(new_session, p1, p2):
    from ..views.default import register_view
    register_results = register_view(dummy_post_request(new_session, {
        'username': 'username',
        'password': p1,
        'password_confirm': p2
    }))
    assert register_results == {'unmatched_password': True}
