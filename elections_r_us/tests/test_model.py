"""Test models."""

from __future__ import unicode_literals
import pytest

from ..models import User, FavoriteCandidate


@pytest.fixture
def test_user():
    return User(username='user', password=b'password')


def test_user_gets_added(new_session, test_user):
    """Test user gets added to database."""
    new_session.add(test_user)
    new_session.flush()
    assert len(new_session.query(User).all()) == 1


def test_user_stores_username(new_session, test_user):
    """Test user's username gets added to database."""
    new_session.add(test_user)
    new_session.flush()
    assert new_session.query(User).first().username == test_user.username


def test_user_stores_password(new_session, test_user):
    """Test user's password gets added to database."""
    new_session.add(test_user)
    new_session.flush()
    assert new_session.query(User).first().password == test_user.password


def make_test_candidate(userid):
    return FavoriteCandidate(
        userid=userid,
        candidatename='Gary Johnson / Bill Weld',
        party='Libertarian party',
        office='President/Vice President',
        website='http://www.johnsonweld.com',
        email='info@johnsonweld.com',
        phone='801-303-7922'
    )


FAVORITE_CANDIDATE_FIELDS = [
    'userid', 'candidatename', 'party', 'office', 'website', 'email', 'phone'
]


@pytest.mark.parametrize('field', FAVORITE_CANDIDATE_FIELDS)
def test_candidate_stores_field(session_with_user, field):
    """Test candidate gets added to a user's favorites."""
    session, username, password = session_with_user
    userid = session.query(User).filter(User.username == username).first().id
    test_candidate = make_test_candidate(userid)
    session.add(test_candidate)
    session.flush()
    stored_model = session.query(FavoriteCandidate).first()
    assert getattr(stored_model, field) == getattr(test_candidate, field)
