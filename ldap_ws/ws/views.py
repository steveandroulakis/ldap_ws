import json

from django.http import HttpResponse
from django.http import Http404

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
