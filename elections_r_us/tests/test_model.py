"""Test models."""

from __future__ import unicode_literals

from ..models import User


def test_user_gets_added(new_session):
    """Test user gets added to database."""
    model = User(username='user', password=b'password')
    new_session.add(model)
    new_session.flush()
    assert(len(new_session.query(User).all()) == 1)


def test_user_stores_username(new_session):
    """Test user's username gets added to database."""
    model = User(username='user', password=b'password')
    new_session.add(model)
    new_session.flush()
    assert(new_session.query(User).first().username == 'user')


def test_user_stores_password(new_session):
    """Test user's password gets added to database."""
    model = User(username='user', password=b'password')
    new_session.add(model)
    new_session.flush()
    assert(new_session.query(User).first().password == b'password')
