from models import User
from passlib.apps import custom_app_context as pwd_context

def create_user(session, username, password):
    session.add(User(
        username=username,
        password=pwd_context.encrypt(password)
    ))


def check_login(session, username, password):
    try:
        query = session.query(User).filter(User.username == username).first()
        return pwd_context.verify(password, query.password)
    except AttributeError:
        return False
