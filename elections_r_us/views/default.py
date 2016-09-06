from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid.security import remember, forget

from ..models import User
from ..security import check_login, create_user


class BadUsername(Exception):
    pass


class BadPassword(Exception):
    pass


class UnmatchedPassword(Exception):
    pass


def verify_registration(username, password, password_confirm):
    if username == '':
        raise BadUsername()
    for c in username:
        if c != '_' and not c.isalnum():
            raise BadUsername()
    if len(password) < 6:
        raise BadPassword()
    if password != password_confirm:
        raise UnmatchedPassword()
    return True


def user_exists(session, username):
    query = session.query(User).filter(User.username == username).all()
    return len(query) > 0


@view_config(route_name='home', renderer='templates/home.jinja2')
def home_view(request):
    return {}


@view_config(route_name='login', renderer="templates/login.jinja2")
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if check_login(request.dbsession, username, password):
            return HTTPFound('/', headers=remember(request, username))
        else:
            return {'login_failure': True}
    return {}


@view_config(route_name='logout', permission='login')
def logout_view(request):
    """Log user out."""
    return HTTPFound(location='/', headers=forget(request))


@view_config(route_name='register', renderer="templates/register.jinja2")
def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']
        try:
            verify_registration(username, password, password_confirm)
        except BadUsername:
            return {'bad_username': True}
        except BadPassword:
            return {'bad_password': True}
        except UnmatchedPassword:
            return {'unmatched_password': True}
        create_user(request.dbsession, username, password)
        return HTTPFound('/')
    return {}
