"""Test models."""

from __future__ import unicode_literals
import pytest

from ..models import User


@pytest.fixture
def example_user():
    info = dict(
        username='user',
        password=b'test password',
        email='test@test.com',
        address='test address'
    )
    return info, User(
        username=info['username'],
        password=info['password'],
        email=info['email'],
        address=info['address']
    )


def test_user_gets_added(new_session, example_user):
    """Test user gets added to database."""
    info, model = example_user
    new_session.add(model)
    new_session.flush()
    assert len(new_session.query(User).all()) == 1


def test_user_stores_username(new_session, example_user):
    """Test user's username gets added to database."""
    info, model = example_user
    new_session.add(model)
    new_session.flush()
    assert new_session.query(User).first().username == info['username']


def test_user_stores_password(new_session, example_user):
    """Test user's password gets added to database."""
    info, model = example_user
    new_session.add(model)
    new_session.flush()
    assert new_session.query(User).first().password == info['password']


def test_user_stores_address(new_session, example_user):
    """Test user's password gets added to database."""
    info, model = example_user
    new_session.add(model)
    new_session.flush()
    assert new_session.query(User).first().address == info['address']


def test_user_stores_email(new_session, example_user):
    """Test user's password gets added to database."""
    info, model = example_user
    new_session.add(model)
    new_session.flush()
    assert new_session.query(User).first().email == info['email']
