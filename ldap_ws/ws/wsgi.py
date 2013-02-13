"""
WSGI config for ldap_ws project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import sys, os
__this__ = os.getcwd()

def setup_python_path():    
    base = __this__
    sources = os.path.join(base, 'parts')
    eggs = os.path.join(base, 'eggs')

    paths = []
    paths.append(os.path.dirname(__this__))

    for src in os.listdir(sources):
        paths.append(os.path.join(__this__, 'parts', src))

    for egg in os.listdir(eggs):
        paths.append(os.path.join(__this__, 'eggs', egg))

    sys.path[0:0] = paths

setup_python_path()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ldap_ws.settings")

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Apply WSGI middleware here.
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)
