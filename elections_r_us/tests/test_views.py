"""Tests for views."""

from __future__ import unicode_literals
import pytest
from pyramid.httpexceptions import HTTPFound
from pyramid import testing

from .conftest import dummy_post_request


VALID_LOGINS = [
    ('username', 'password'),
    ('user_name', 'eoae8uadh%$  '),
    ('User_name764', 'adiug98'),
    ('0234867', '8419tagsh')
]


VALID_PASSWORDS = [
    'password',
    'eoae8uadh%$  ',
    'adiug98',
    '8419tagsh'
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
    ('a'*10, 'A'*10),
    ('asgasdh0', 'ahdfharth')
]


def test_valid_registration(valid_registration):
    """Test that verify_registration returns positive with good info."""
    from ..views.default import verify_registration
    assert verify_registration(valid_registration)


@pytest.mark.parametrize('username', BAD_USERNAMES)
def test_bad_username(username, valid_registration):
    """Test that verify_registration rejects a bad username."""
    from ..views.default import verify_registration, BadLoginInfo
    with pytest.raises(BadLoginInfo):
        verify_registration(valid_registration._replace(username=username))


@pytest.mark.parametrize('password', BAD_PASSWORDS)
def test_bad_password(password, valid_registration):
    """Test that verify_registration rejects a bad password."""
    from ..views.default import verify_registration, BadLoginInfo
    valid_registration = valid_registration._replace(
        password=password,
        password_confirm=password
    )
    with pytest.raises(BadLoginInfo):
        verify_registration(valid_registration)


@pytest.mark.parametrize('p1, p2', UNMATCHED_PASSWORDS)
def test_unmatched_password(p1, p2, valid_registration):
    """Test that verify_registration rejects unmatched passwords."""
    from ..views.default import verify_registration, BadLoginInfo
    valid_registration = valid_registration._replace(
        password=p1,
        password_confirm=p2
    )
    with pytest.raises(BadLoginInfo):
        verify_registration(valid_registration)


def test_login_view_logged_in(session_with_user):
    """Test login view redirects while logged in."""
    from ..views.default import login_view
    session, username, password = session_with_user
    login_results = login_view(dummy_post_request(session, {
        'username': username,
        'password': password
    }))
    assert isinstance(login_results, HTTPFound)


def test_build_address_has_street():
    """Test that build_address retains the street parameter."""
    from ..views.default import build_address
    assert 'street' in build_address('street', 'b', 'c', 'd')


def test_build_address_has_city():
    """Test that build_address retains the city parameter."""
    from ..views.default import build_address
    assert 'city' in build_address('a', 'city', 'c', 'd')


def test_build_address_has_state():
    """Test that build_address retains the state parameter."""
    from ..views.default import build_address
    assert 'state' in build_address('a', 'c', 'state', 'd')


def test_build_address_has_zip():
    """Test that build_address retains the zip parameter."""
    from ..views.default import build_address
    assert '99920' in build_address('a', 'b', 'c', '99920')


def registration_input_to_dict(registration_input):
    """Helper function for creating POSTs to register_view."""
    return {
        'username': registration_input.username,
        'password': registration_input.password,
        'password_confirm': registration_input.password_confirm,
        'email': registration_input.email,
        'street': registration_input.street,
        'city': registration_input.city,
        'state': registration_input.state,
        'zip': registration_input.zip
    }


def test_register_view_success(new_session, valid_registration):
    """Test that register view success redirects."""
    from ..views.default import register_view
    register_results = register_view(dummy_post_request(
        new_session, registration_input_to_dict(valid_registration)
    ))
    assert isinstance(register_results, HTTPFound)


def test_register_view_success_creates_user(new_session, valid_registration):
    """Test that register_view creates a user when successful."""
    from ..views.default import register_view
    from ..models import User
    register_view(dummy_post_request(
        new_session, registration_input_to_dict(valid_registration)
    ))
    stored_username = new_session.query(User).first().username
    assert stored_username == valid_registration.username


@pytest.mark.parametrize('username', BAD_USERNAMES)
def test_register_view_bad_username(new_session, username, valid_registration):
    """Test that register_view reports bad usernames."""
    from ..views.default import register_view
    registration_input = valid_registration._replace(username=username)
    register_results = register_view(dummy_post_request(
        new_session, registration_input_to_dict(registration_input)
    ))
    assert register_results['failure'] == 'bad username'


@pytest.mark.parametrize('password', BAD_PASSWORDS)
def test_register_view_bad_password(new_session, password, valid_registration):
    """Test that register_view reports bad passwords."""
    from ..views.default import register_view
    registration_input = valid_registration._replace(
        password=password,
        password_confirm=password
    )
    register_results = register_view(dummy_post_request(
        new_session, registration_input_to_dict(registration_input)
    ))
    assert register_results['failure'] == 'bad password'


@pytest.mark.parametrize('p1, p2', UNMATCHED_PASSWORDS)
def test_register_view_unmatched_pass(new_session, p1, p2, valid_registration):
    """Test that register_view reports unmatched passwords."""
    from ..views.default import register_view
    registration_input = valid_registration._replace(
        password=p1,
        password_confirm=p2
    )
    register_results = register_view(dummy_post_request(
        new_session, registration_input_to_dict(registration_input)
    ))
    assert register_results['failure'] == 'unmatched passwords'


@pytest.mark.parametrize('new_password', VALID_PASSWORDS)
def test_password_change_success(session_with_user, new_password):
    """Test that password_change_view shows success."""
    from ..views.default import password_change_view
    session, username, old_password = session_with_user
    result = password_change_view(dummy_post_request(session, {
        'old_password': old_password,
        'new_password': new_password,
        'password_confirm': new_password
    }))
    assert 'password_changed' in result


@pytest.mark.parametrize('new_password', VALID_PASSWORDS)
def test_password_change_updates_password(session_with_user, new_password):
    """Test that password_change_view changes the password."""
    from ..views.default import password_change_view
    from ..security import pwd_context
    from ..models import User
    session, username, old_password = session_with_user
    password_change_view(dummy_post_request(session, {
        'old_password': old_password,
        'new_password': new_password,
        'password_confirm': new_password
    }))
    assert pwd_context.verify(
        new_password,
        session.query(User).filter(User.username == username).first().password
    )


@pytest.mark.parametrize('new_password', BAD_PASSWORDS)
def test_password_change_bad_password(session_with_user, new_password):
    """Test that password_change_view rejects a bad password."""
    from ..views.default import password_change_view
    session, username, old_password = session_with_user
    response = password_change_view(dummy_post_request(session, {
        'old_password': old_password,
        'new_password': new_password,
        'password_confirm': new_password
    }))
    assert response['failure'] == 'bad password'


@pytest.mark.parametrize('p1, p2', UNMATCHED_PASSWORDS)
def test_password_change_unmatched_password(session_with_user, p1, p2):
    """Test that password_change_view rejects a unmatched passwords."""
    from ..views.default import password_change_view
    session, username, old_password = session_with_user
    request = dummy_post_request(session, {
        'old_password': old_password,
        'new_password': p1,
        'password_confirm': p2
    })
    response = password_change_view(request)
    assert response['failure'] == 'unmatched passwords'


def test_password_change_failed_login(session_with_user):
    """Test that password_change_view rejects without correct old password."""
    from ..views.default import password_change_view
    session, username, old_password = session_with_user
    new_password = 'good password'
    request = dummy_post_request(session, {
        'old_password': old_password + '!',
        'new_password': new_password,
        'password_confirm': new_password
    })
    response = password_change_view(request)
    assert response['failure'] == 'login_failure'


@pytest.mark.parametrize('password', VALID_PASSWORDS)
def test_password_verify_success(password):
    """Test verify password returns True for valid passwords."""
    from ..views.default import verify_password
    assert verify_password(password, password)


@pytest.mark.parametrize('password', BAD_PASSWORDS)
def test_password_verify_bad(password):
    """Test verify password returns False for bad passwords."""
    from ..views.default import verify_password, BadLoginInfo
    with pytest.raises(BadLoginInfo):
        verify_password(password, password)


@pytest.mark.parametrize('p1, p2', UNMATCHED_PASSWORDS)
def test_password_verify_unmatched(p1, p2):
    """Test verify password returns False for unmatched passwords."""
    from ..views.default import verify_password, BadLoginInfo
    with pytest.raises(BadLoginInfo):
        verify_password(p1, p2)


ADDRESSES = [
    '901 12th Avenue Seattle WA',
    '7600 212th St SW, Edmonds, WA 98026'
]


BAD_ADDRESSES = [  # addresses for which the Google API has no info
    '1330 NE Ford St McMinnville OR'
]


@pytest.mark.parametrize('address', ADDRESSES)
def test_consume_api_success(address):
    """Test that the API returns information for addresses."""
    from ..views.default import get_civic_info
    assert get_civic_info(address)


def test_favorite_candidate_returns_dict(favorite_candidate_post_results):
    """Test that the API returns information for addresses."""
    session, results = favorite_candidate_post_results
    assert isinstance(results, HTTPFound)


def test_favorite_candidate_view_stores(favorite_candidate_post_results):
    """Test that favoriting candidates stores them."""
    from ..models import FavoriteCandidate
    session, results = favorite_candidate_post_results
    query = session.query(FavoriteCandidate)
    assert len(query.all()) == 1


def test_favorite_referendum_redirects(favorite_referendum_post_results):
    """Fixture for a user with a favorited referendum"""
    session, results = favorite_referendum_post_results
    assert isinstance(results, HTTPFound)


def test_favorite_referendum_view_stores(favorite_referendum_post_results):
    """Test that favoriting referendum stores it."""
    from ..models import FavoriteReferendum
    session, results = favorite_referendum_post_results
    query = session.query(FavoriteReferendum)
    assert len(query.all()) == 1


def test_profile_view_favorite_candidates(favorite_candidate_post_results):
    """Test that profile view gives favorited candidates."""
    from ..views.default import profile_view
    request = testing.DummyRequest()
    request.dbsession, _ = favorite_candidate_post_results
    assert len(profile_view(request)['candidates']) > 0


def test_home_view_logged_in_address(session_with_user):
    """Test that home view while logged in gives address."""
    from ..views.default import home_view
    request = testing.DummyRequest()
    request.dbsession, _, _ = session_with_user
    assert 'address' in home_view(request)


def test_about(session_with_user):
    from ..views.default import about_view
    assert about_view(testing.DummyRequest()) == {}


def test_user_profile_has_username(session_with_user):
    from ..views.default import user_profile
    request = testing.DummyRequest()
    request.dbsession, username, password = session_with_user
    assert request.authenticated_userid is not None
    assert 'username' in user_profile(request)


@pytest.mark.parametrize('address', ADDRESSES)
def test_result_list_view_address(address, new_session):
    from ..views.default import result_list_view
    response = result_list_view(dummy_post_request(new_session, {
        'address': address
    }))
    assert isinstance(response, dict)


def test_results_list_view_search_form(new_session):
    from ..views.default import result_list_view
    response = result_list_view(dummy_post_request(new_session, {
        'street': '7600 212th St SW',
        'city': 'Edmonds',
        'state': 'WA',
        'zip': '98026',
    }))
    assert isinstance(response, dict)


def test_login_view_failure(unauthenticated_session):
    """Test logging in."""
    from ..views.default import login_view
    request = login_view(dummy_post_request(unauthenticated_session, {
        'username': 'username',
        'password': 'passwor',
    }))
    assert 'failure' in request


def test_home(unauthenticated_session_with_user):
    from ..views.default import home_view
    request = testing.DummyRequest()
    request.dbsession, username, password = unauthenticated_session_with_user
    assert home_view(request) == {}


def test_login_view_success(unauthenticated_session_with_user):
    """Test login view redirects on success"""
    from ..views.default import login_view
    session, username, password = unauthenticated_session_with_user
    login_results = login_view(dummy_post_request(session, {
        'username': username,
        'password': password
    }))
    assert isinstance(login_results, HTTPFound)
