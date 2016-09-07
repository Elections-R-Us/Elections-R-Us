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
    from ..views.default import verify_registration
    assert verify_registration(valid_registration)


@pytest.mark.parametrize('username', BAD_USERNAMES)
def test_bad_username(username, valid_registration):
    from ..views.default import verify_registration, BadLoginInfo
    with pytest.raises(BadLoginInfo):
        verify_registration(valid_registration._replace(username=username))


@pytest.mark.parametrize('password', BAD_PASSWORDS)
def test_bad_password(password, valid_registration):
    from ..views.default import verify_registration, BadLoginInfo
    valid_registration = valid_registration._replace(
        password=password,
        password_confirm=password
    )
    with pytest.raises(BadLoginInfo):
        verify_registration(valid_registration)


@pytest.mark.parametrize('p1, p2', UNMATCHED_PASSWORDS)
def test_unmatched_password(p1, p2, valid_registration):
    from ..views.default import verify_registration, BadLoginInfo
    valid_registration = valid_registration._replace(
        password=p1,
        password_confirm=p2
    )
    with pytest.raises(BadLoginInfo):
        verify_registration(valid_registration)


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
    assert login_results['failure'] == 'login_failure'


def registration_input_to_dict(registration_input):
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


def test_build_address_has_street():
    from ..views.default import build_address
    assert 'street' in build_address('street', 'b', 'c', 'd')


def test_build_address_has_city():
    from ..views.default import build_address
    assert 'city' in build_address('a', 'city', 'c', 'd')


def test_build_address_has_state():
    from ..views.default import build_address
    assert 'state' in build_address('a', 'c', 'state', 'd')


def test_build_address_has_zip():
    from ..views.default import build_address
    assert '99920' in build_address('a', 'b', 'c', '99920')


def test_register_view_success(new_session, valid_registration):
    from ..views.default import register_view
    register_results = register_view(dummy_post_request(
        new_session, registration_input_to_dict(valid_registration)
    ))
    assert isinstance(register_results, HTTPFound)


def test_register_view_success_creates_user(new_session, valid_registration):
    from ..views.default import register_view
    from ..models import User
    register_view(dummy_post_request(
        new_session, registration_input_to_dict(valid_registration)
    ))
    stored_username = new_session.query(User).first().username
    assert stored_username == valid_registration.username


@pytest.mark.parametrize('username', BAD_USERNAMES)
def test_register_view_bad_username(new_session, username, valid_registration):
    from ..views.default import register_view
    registration_input = valid_registration._replace(username=username)
    register_results = register_view(dummy_post_request(
        new_session, registration_input_to_dict(registration_input)
    ))
    assert register_results['failure'] == 'bad username'


@pytest.mark.parametrize('password', BAD_PASSWORDS)
def test_register_view_bad_password(new_session, password, valid_registration):
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
    from ..views.default import password_change_view
    session, username, old_password = session_with_user
    new_password = 'good password'
    request = dummy_post_request(session, {
        'old_password': old_password + '!',
        'new_password': new_password,
        'password_confirm': new_password
    })
    response = password_change_view(request)
    assert response['failure'] == 'failed login'


@pytest.mark.parametrize('password', VALID_PASSWORDS)
def test_password_verify_success(password):
    from ..views.default import verify_password
    assert verify_password(password, password)


@pytest.mark.parametrize('password', BAD_PASSWORDS)
def test_password_verify_bad(password):
    from ..views.default import verify_password, BadLoginInfo
    with pytest.raises(BadLoginInfo):
        verify_password(password, password)


@pytest.mark.parametrize('p1, p2', UNMATCHED_PASSWORDS)
def test_password_verify_unmatched(p1, p2):
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
    from ..views.default import get_civic_info
    assert get_civic_info(address)


@pytest.fixture
def favorite_candidate_post_results(session_with_user):
    from ..views.default import favorite_candidate_view
    from ..models import User
    session, username, password = session_with_user
    userid = session.query(User).filter(User.username == username).first().id
    return session, favorite_candidate_view(dummy_post_request(
        session, {
            'userid': userid,
            'candidatename': 'Gary Johnson / Bill Weld',
            'party': 'Libertarian party',
            'office': 'President/Vice President',
            'website': 'http://www.johnsonweld.com',
            'email': 'info@johnsonweld.com',
            'phone': '801-303-7922'
        }))


def test_favorite_candidate_returns_dict(favorite_candidate_post_results):
    session, results = favorite_candidate_post_results
    assert isinstance(results, dict)


def test_favorite_candidate_view_stores(favorite_candidate_post_results):
    from ..models import FavoriteCandidate
    session, results = favorite_candidate_post_results
    query = session.query(FavoriteCandidate)
    assert len(query.all()) == 1


def test_profile_view_favorite_candidates(favorite_candidate_post_results):
    from ..views.default import profile_view
    request = testing.DummyRequest()
    request.dbsession, _ = favorite_candidate_post_results
    assert len(profile_view(request)['candidates']) > 0
