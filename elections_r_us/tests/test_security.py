from __future__ import unicode_literals

from ..models import User


def test_user_gets_created(new_session):
    from ..security import create_user
    create_user(new_session, 'username', 'password')
    assert len(new_session.query(User).all()) == 1


def test_user_can_login(session_with_user):
    from ..security import check_login
    assert check_login(*session_with_user)


def test_nonexistent_user_login_fails(new_session):
    from ..security import check_login
    assert not check_login(new_session, 'hello', 'world')
