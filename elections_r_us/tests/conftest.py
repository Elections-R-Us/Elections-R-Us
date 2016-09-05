"""Configuration for pytest."""

import os
import pytest
import transaction
from pyramid import testing
from elections_r_us.security import pwd_context

from ..models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    User
)
from ..models.meta import Base


@pytest.fixture(scope="session")
def sqlengine(request):
    """Creates a SQL engine specifically for testing (which is destroyed afterwards)."""
    config = testing.setUp(settings={
        'sqlalchemy.url': os.environ["DATABASE_URL"]
    })
    config.include("..models")
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
    session_factory = get_session_factory(sqlengine)
    session = get_tm_session(session_factory, transaction.manager)

    def teardown():
        transaction.abort()

    request.addfinalizer(teardown)
    return session


@pytest.fixture
def session_with_user(new_session):
    username = 'username'
    password = 'password'
    new_session.add(User(
        username=username,
        password=pwd_context.encrypt(password)
    ))
    new_session.flush()
    return new_session, username, password
