from pyramid.response import Response


def my_view(request):
    return Response('hi')


class BadUsername(Exception):
    pass


def verify_registration(username, password, password_confirm):
    if username == '':
        raise BadUsername()
    for c in username:
        if c != '_' and not c.isalnum():
            raise BadUsername()
    return True
