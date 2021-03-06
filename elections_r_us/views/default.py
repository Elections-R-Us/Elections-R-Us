import os
from collections import namedtuple

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid.security import remember, forget

from googleapiclient.errors import HttpError
import googleapiclient.discovery as discovery

from ..models import User, FavoriteCandidate, FavoriteReferendum
from ..security import check_login, create_user, change_password
from .test_dict import test_dict

ELECTION_ID = 5000  # id for the current election (according to the google api)


_RegistrationInput = namedtuple(
    'credentials',
    'username password password_confirm email street city state zip'
)


class RegistrationInput(_RegistrationInput):
    """RegistrationInput represents the input for the registration form.

    This is for unprocessed inputs-- eventually (if the
    RegistrationInput is valid), the relevant data is transfered to a
    UserInfo object."""
    pass


class UserInfo(namedtuple('credentials', 'username password email address')):
    """UserInfo represents a user as it is modeled in the database.

    This is for a user which has already been added to the database,
    or one which is about to be added."""
    pass


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


@view_config(route_name='home', renderer='templates/address_entry.jinja2')
def home_view(request):
    username = request.authenticated_userid
    if request.authenticated_userid:
        query = request.dbsession.query(User)
        address = query.filter(User.username == username).first().address
        return {'address': address}
    return {}


@view_config(route_name='about_us', renderer='templates/about_us.jinja2')
def about_view(request):
    return {}


@view_config(route_name='login', renderer="templates/login.jinja2")
def login_view(request):
    if request.authenticated_userid:
        return HTTPFound('/')
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


def build_address(street, city, state, zip_code):
    return '{}, {}, {} {}'.format(street, city, state, zip_code)


@view_config(route_name='register', renderer="templates/register.jinja2")
def register_view(request):
    if request.method == 'POST':
        credentials = RegistrationInput(
            username=request.POST['username'],
            password=request.POST['password'],
            password_confirm=request.POST['password_confirm'],
            street=request.POST['street'],
            city=request.POST['city'],
            state=request.POST['state'],
            zip=request.POST['zip'],
            email=request.POST['email']
        )
        query = request.dbsession.query(User)
        if query.filter(User.username == credentials.username).first():
            return failure_info('username taken')
        try:
            verify_registration(credentials)
        except BadLoginInfo as bad:
            return failure_info(bad.info)
        create_user(request.dbsession, UserInfo(
            username=credentials.username,
            password=credentials.password,
            email=credentials.email,
            address=build_address(
                credentials.street,
                credentials.city,
                credentials.state,
                credentials.zip,
            )))
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
            return failure_info('login_failure')
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


def post_to_favorite_candidate(post_dict):
    return FavoriteCandidate(
        candidatename=post_dict['candidatename'],
        office=post_dict['office']
    )


def post_to_favorite_referendum(post_dict):
    return FavoriteReferendum(
        title=post_dict['title'],
        brief=post_dict['brief'],
        position=post_dict['position'],
    )


def get_userid_from_name(session, username):
    return session.query(User).filter(User.username == username).first().id


@view_config(route_name='favorite')
def favorite_view(request):
    if request.method == 'POST':
        if request.POST['type'] == 'referendum':
            model = post_to_favorite_referendum(request.POST)
        else:
            model = post_to_favorite_candidate(request.POST)
        model.userid = get_userid_from_name(
            request.dbsession,
            request.authenticated_userid
        )
        request.dbsession.add(model)
    return HTTPFound('/user_profile')


@view_config(route_name='results_list',
             renderer='templates/results_list.jinja2')
def result_list_view(request):
    if request.method == "POST":
        if 'address' in request.POST:
            address = request.POST['address']
        else:
            address = build_address(
                request.POST['street'],
                request.POST['city'],
                request.POST['state'],
                request.POST['zip']
            )
        return get_civic_info(address) or {}
    return {}


def profile_view(request):
    query = request.dbsession.query(User)
    user = query.filter(User.username == request.authenticated_userid).first()
    return {
        'candidates': user.favoritecandidates
    }


@view_config(
    route_name='user_profile',
    renderer='templates/user_profile.jinja2',
    permission='login'
)
def user_profile(request):
    username = request.authenticated_userid
    query = request.dbsession.query(User)
    user = query.filter(User.username == username).first()
    return {
        'username': user.username,
        'email': user.email,
        'address': user.address,
        'candidates': user.favoritecandidates,
        'referendums': user.favoritereferendums,
    }
