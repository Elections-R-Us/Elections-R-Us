"""Configuration for pytest."""

import os
import pytest
import transaction
from pyramid import testing
from ..security import pwd_context
from ..views.default import UserInfo, RegistrationInput
from webtest import TestApp as _TestApp
from .. import main


from ..models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    User
)
from ..models.meta import Base


@pytest.fixture(scope="function")
def app():
    my_app = main({})
    app = _TestApp(my_app)
    return app


def make_sqlengine(request, authenticated):
    """Creates a SQL engine for testing."""
    config = testing.setUp(settings={
        'sqlalchemy.url': os.environ["DATABASE_URL"]
    })
    config.include("..models")
    if authenticated:
        config.testing_securitypolicy(userid='username')
    settings = config.get_settings()
    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    def teardown():
        testing.tearDown()
        transaction.abort()
        Base.metadata.drop_all(engine)

    request.addfinalizer(teardown)
    return engine


@pytest.fixture(scope="session")
def sqlengine(request):
    return make_sqlengine(request, True)


@pytest.fixture(scope="session")
def unauthenticated_sqlengine(request):
    return make_sqlengine(request, False)


def make_new_session(sql, request):
    """A new database session."""
    session_factory = get_session_factory(sql)
    session = get_tm_session(session_factory, transaction.manager)

    def teardown():
        transaction.abort()

    request.addfinalizer(teardown)
    return session


@pytest.fixture(scope="function")
def new_session(sqlengine, request):
    """A new database session."""
    return make_new_session(sqlengine, request)


@pytest.fixture(scope="function")
def unauthenticated_session(unauthenticated_sqlengine, request):
    """An unauthenticated new database session."""
    return make_new_session(unauthenticated_sqlengine, request)


def make_session_with_user(session):
    """A database session with a user attached to it."""
    username = 'username'
    password = 'password'
    session.add(User(
        username=username,
        password=pwd_context.encrypt(password),
        email='test@example.org',
        address='test address',
    ))
    session.flush()
    return session, username, password


@pytest.fixture(scope="function")
def session_with_user(new_session):
    return make_session_with_user(new_session)


@pytest.fixture(scope="function")
def unauthenticated_session_with_user(unauthenticated_session):
    return make_session_with_user(unauthenticated_session)


@pytest.fixture
def valid_user():
    return UserInfo(
        username='user',
        password='secure password',
        email='email@example.org',
        address='901 12th Avenue, Seattle, WA 98503'
    )


@pytest.fixture
def valid_registration():
    return RegistrationInput(
        username='user',
        password='secure password',
        password_confirm='secure password',
        email='email@example.org',
        street='901 12th Avenue',
        city='Seattle',
        state='WA',
        zip='98503'
    )


@pytest.fixture
def favorite_candidate_post_results(session_with_user):
    """Test that the API returns information for addresses."""
    from ..views.default import favorite_view
    session, username, password = session_with_user
    return session, favorite_view(dummy_post_request(
        session, {
            'type': 'general election',
            'candidatename': 'Gary Johnson / Bill Weld',
            'office': 'President/Vice President',
        }))


@pytest.fixture
def favorite_referendum_post_results(session_with_user):
    """Fixture for a user with a favorited referendum"""
    from ..views.default import favorite_view
    session, username, password = session_with_user
    return session, favorite_view(dummy_post_request(
        session, {
            'type': 'referendum',
            'title': 'Initiative Measure No. 1433',
            'brief': 'concerns labor standards',
            'position': 'Yes'
        }))


def dummy_post_request(new_session, params):
    """Dummy post request creator for tests."""
    dummy = testing.DummyRequest(post=params)
    dummy.dbsession = new_session
    return dummy
