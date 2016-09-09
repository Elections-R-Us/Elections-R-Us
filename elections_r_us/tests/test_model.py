"""Test models."""

from __future__ import unicode_literals
import pytest

from ..models import User, FavoriteCandidate, FavoriteReferendum


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


def make_test_candidate(userid):
    return FavoriteCandidate(
        userid=userid,
        candidatename='Gary Johnson / Bill Weld',
        office='President/Vice President',
    )


FAVORITE_CANDIDATE_FIELDS = [
    'candidatename', 'office',
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


def test_favoriting_candidate_without_existent_user(new_session):
    """Test the database rejects favoriting a candidate without a user."""
    from sqlalchemy.exc import IntegrityError
    new_session.add(make_test_candidate(666))
    with pytest.raises(IntegrityError):
        new_session.flush()


def make_test_referendum(userid):
    return FavoriteReferendum(
        userid=userid,
        title='Initiative Measure No. 1433',
        brief='concerns labor standards',
        position='Yes',
    )


FAVORITE_REFERENDUM_FIELDS = [
    'title', 'brief', 'position'
]


@pytest.mark.parametrize('field', FAVORITE_REFERENDUM_FIELDS)
def test_referendum_stores_field(session_with_user, field):
    """Test candidate gets added to a user's favorites."""
    session, username, password = session_with_user
    userid = session.query(User).filter(User.username == username).first().id
    test_referendum = make_test_referendum(userid)
    session.add(test_referendum)
    session.flush()
    stored_model = session.query(FavoriteReferendum).first()
    assert getattr(stored_model, field) == getattr(test_referendum, field)


def test_favoriting_referendum_without_existent_user(new_session):
    """Test the database rejects favoriting a candidate without a user."""
    from sqlalchemy.exc import IntegrityError
    new_session.add(make_test_referendum(666))
    with pytest.raises(IntegrityError):
        new_session.flush()
