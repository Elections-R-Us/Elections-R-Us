from models import User
from passlib.apps import custom_app_context as pwd_context

def create_user(session, username, password):
    """Add a new user to the database.

    session is expected to be a dbsession, username and password are
    expected to be (unencrypted) unicode strings."""
    session.add(User(
        username=username,
        password=pwd_context.encrypt(password)
    ))


def check_login(session, username, password):
    """Return whether username and password match in the database.

    If username is not present, returns False."""
    try:
        query = session.query(User).filter(User.username == username).first()
        return pwd_context.verify(password, query.password)
    except AttributeError:
        return False
