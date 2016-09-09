"""Tests for security.py"""

from __future__ import unicode_literals

from ..models import User


def test_user_gets_created(new_session, valid_user):
    """Test that after create_user adds to the database."""
    from ..security import create_user
    create_user(new_session, valid_user)
    assert len(new_session.query(User).all()) == 1


def test_user_can_login(session_with_user):
    """Test that check_login returns True with the correct login."""
    from ..security import check_login
    assert check_login(*session_with_user)


def test_nonexistent_user_login_fails(new_session):
    """Test check_login returns False when the username isn't present."""
    from ..security import check_login
    assert not check_login(new_session, 'hello', 'world')


def test_bad_password_login_fails(session_with_user):
    """Test check_login returns False when the password doesn't match."""
    from ..security import check_login
    session, username, password = session_with_user
    assert not check_login(session, username, password + 'not!')


def test_change_password(session_with_user):
    """Test changing a password for a user."""
    from ..security import check_login, change_password
    session, username, password = session_with_user
    new_password = password + '!'
    change_password(session, username, new_password)
    assert check_login(session, username, new_password)


def test_change_password_new_overwrites(session_with_user):
    """Test that one can't use an old password after changing."""
    from ..security import check_login, change_password
    session, username, password = session_with_user
    new_password = password + '!'
    change_password(session, username, new_password)
    assert not check_login(session, username, password)
