import json
import urllib

from django.http import HttpResponse
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt

from ldap_ws.ws.ldap_lib import ldap_lib


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = json.dumps(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def info_by_username(request, username):
    ld = ldap_lib.ldap_auth()
    user = ld.getUserById(username)
    if user:
        return JSONResponse(user)
    else:
        raise Http404


def info_by_email(request):
    email = request.GET.get('email', '')
    email = urllib.unquote_plus(email)

    ld = ldap_lib.ldap_auth()
    user = ld.getUsernameByEmail(email)
    if user:
        return JSONResponse(user)
    else:
        raise Http404


@csrf_exempt
def authenticate(request):
    if not request.method == 'POST':
        return JSONResponse('', status=400)

    if 'username' in request.POST and \
            'password' in request.POST:

        username = request.POST['username']
        password = request.POST['password']

    else:
        return JSONResponse('', status=400)

    ld = ldap_lib.ldap_auth()
    user = ld.authenticate(username, password)
    if user:
        return JSONResponse(user)
    else:
        raise Http404
