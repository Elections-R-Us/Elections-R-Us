import os
from collections import namedtuple

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid.security import remember, forget

from googleapiclient.errors import HttpError
import googleapiclient.discovery as discovery

from ..models import User
from ..security import check_login, create_user, change_password


registration_input = namedtuple(
    'credentials',
    'username password password_confirm email address'
)


ELECTION_ID = 5000


class BadLoginInfo(Exception):
    def __init__(self, info):
        self.info = info


def failure_info(reason):
    return {'failure': reason}


def verify_password(password, password_confirm):
    if len(password) < 6:
        raise BadLoginInfo('bad password')
    if password != password_confirm:
        raise BadLoginInfo('unmatched passwords')
    return True


def verify_registration(inp):
    if inp.username == '':
        raise BadLoginInfo('bad username')
    for c in inp.username:
        if c != '_' and not c.isalnum():
            raise BadLoginInfo('bad username')
    return verify_password(inp.password, inp.password_confirm)


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
            return failure_info('login_failure')
    return {}


@view_config(route_name='logout', permission='login')
def logout_view(request):
    """Log user out."""
    return HTTPFound(location='/', headers=forget(request))


@view_config(route_name='register', renderer="templates/register.jinja2")
def register_view(request):
    if request.method == 'POST':
        credentials = registration_input(
            username=request.POST['username'],
            password=request.POST['password'],
            password_confirm=request.POST['password_confirm'],
            address=request.POST['address'],
            email=request.POST['email']
        )
        try:
            verify_registration(credentials)
        except BadLoginInfo as bad:
            return failure_info(bad.info)
        create_user(request.dbsession, credentials)
        return HTTPFound(location='/')
    return {}


@view_config(
    route_name='change_password',
    renderer='templates/change_password.jinja2',
    permission='login'
)
def password_change_view(request):
    if request.method == 'POST':
        username = request.authenticated_userid
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
        password_confirm = request.POST['password_confirm']
        try:
            verify_password(new_password, password_confirm)
        except BadLoginInfo as bad:
            return failure_info(bad.info)
        if not check_login(request.dbsession, username, old_password):
            return failure_info('failed login')
        change_password(request.dbsession, username, new_password)
        return {'password_changed': True}
    return {}


def get_civic_info(address):
    civicinfo_service = discovery.build(
        'civicinfo',
        'v2',
        developerKey=os.environ.get('APIKEY')
    )
    info_query = civicinfo_service.elections().voterInfoQuery(
        address=address,
        electionId=ELECTION_ID
    )
    try:
        return info_query.execute()
    except HttpError:
        return None
