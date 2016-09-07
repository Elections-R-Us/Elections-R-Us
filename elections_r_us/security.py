import os

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Everyone, Authenticated, Allow

from passlib.apps import custom_app_context as pwd_context

from .models import User


class Root(object):
    def __init__(self, request):
        """Initialize a new Root."""
        self.request = request

    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, Authenticated, 'login')
    ]


def create_user(session, info):
    """Add a new user to the database.

    session is expected to be a dbsession, username and password are
    expected to be (unencrypted) unicode strings."""
    session.add(User(
        username=info.username,
        password=pwd_context.encrypt(info.password),
        email=info.email,
        address=info.address
    ))


def change_password(session, username, new_password):
    user = session.query(User).filter(User.username == username).first()
    if user is None:
        import pdb; pdb.set_trace()
    user.password = pwd_context.encrypt(new_password)


def check_login(session, username, password):
    """Return whether username and password match in the database.

    If username is not present, returns False."""
    query = session.query(User).filter(User.username == username).first()
    try:
        return pwd_context.verify(password, query.password)
    except AttributeError:  # username not in db
        return False


def includeme(config):
    auth_secret = os.environ.get('AUTH_SECRET', 'secret authentication secret')
    authn_policy = AuthTktAuthenticationPolicy(
        secret=auth_secret,
        hashalg='sha512'
    )
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.set_default_permission('view')
    config.set_root_factory(Root)
