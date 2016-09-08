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


@pytest.fixture(scope="session")
def sqlengine(request):
    """Creates a SQL engine specifically for testing (which is destroyed afterwards)."""
    config = testing.setUp(settings={
        'sqlalchemy.url': os.environ["DATABASE_URL"]
    })
    config.include("..models")
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


@pytest.fixture(scope="function")
def new_session(sqlengine, request):
    """A new database session."""
    session_factory = get_session_factory(sqlengine)
    session = get_tm_session(session_factory, transaction.manager)

    def teardown():
        transaction.abort()

    request.addfinalizer(teardown)
    return session


@pytest.fixture
def session_with_user(new_session):
    """A database session with a user attached to it."""
    username = 'username'
    password = 'password'
    new_session.add(User(
        username=username,
        password=pwd_context.encrypt(password),
        email='test@example.org',
        address='test address',
    ))
    new_session.flush()
    return new_session, username, password


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
