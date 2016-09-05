from pyramid.response import Response


def my_view(request):
    return Response('hi')
