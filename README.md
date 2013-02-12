Simple LDAP RestFUL Web Service
==============

For accessing LDAP information via simple web service

##Installation (linux)

```bash
# as root for ubuntu:

apt-get install python-setuptools

# as root for redhat (eg CentOS)

yum install python-setuptools

git clone https://github.com/steveandroulakis/ldap_ws.git

cd ldap_ws/

python bootstrap.py

bin/buildout -v

bin/django syncdb --noinput --migrate

```

## Notes:
A file called buildout-prod.cfg can be used in place of bin/buildout -v (use bin/buildout -v -c buildout-prod.cfg) to run the application on a MySQL server instead of the default SQLite which may prove slow.

Run bin/supervisord to start the server (running on nginx with uwsgi).

Requires a MySQL server installed and a settings.py created in the ldap_ws/ directory with the relevant MySQL database credentials within.

Also requires packages for python dev, mysql libraries.


