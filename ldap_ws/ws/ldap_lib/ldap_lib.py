# -*- coding: utf-8 -*-
#
# Copyright (c) 2010-2011, Monash e-Research Centre
#   (Monash University, Australia)
# Copyright (c) 2010-2011, VeRSI Consortium
#   (Victorian eResearch Strategic Initiative, Australia)
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    *  Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#    *  Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#    *  Neither the name of the VeRSI, the VeRSI Consortium members, nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE REGENTS AND CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
'''
LDAP Authentication module.

Taken from https://github.com/mytardis/mytardis/blob/master/tardis/tardis_portal/auth/ldap_auth.py

.. moduleauthor:: Gerson Galang <gerson.galang@versi.edu.au>
.. moduleauthor:: Russell Sim <russell.sim@monash.edu>
.. moduleauthor:: Steve Androulakis <steve.androulakis@monash.edu>
'''


import ldap
import logging

from django.conf import settings


class LDAPBackend():
    def __init__(self, name, url, base, login_attr, user_base,
                 user_attr_map, group_id_attr, group_base,
                 group_attr_map, admin_user='', admin_pass=''):

        self.name = name

        # Basic info
        self._url = url
        self._base = base

        # Authenticated bind
        self._admin_user = admin_user
        self._admin_pass = admin_pass

        # Login attribute
        self._login_attr = login_attr

        # User Search
        self._user_base = user_base
        self._user_attr_map = user_attr_map
        self._user_attr_map[self._login_attr] = "id"

        # Group Search
        self._group_id = group_id_attr
        self._group_base = group_base
        self._group_attr_map = group_attr_map
        self._group_attr_map[self._group_id] = "id"

    def _query(self, base, filterstr, attrlist):
        """Safely query LDAP
        """
        l = None
        searchScope = ldap.SCOPE_SUBTREE

        try:
            l = ldap.initialize(self._url)
        except ldap.LDAPError, e:
            logging.error(e.message['desc'], ": ", self._url)
            return None
        l.protocol_version = ldap.VERSION3

        try:
            if self._admin_user and self._admin_pass:
                l.simple_bind(self._admin_user, self._admin_pass)
            else:
                l.simple_bind()
        except ldap.LDAPError, e:
            logging.error(e.args[0]['desc'])
            if l:
                l.unbind_s()
            return None

        try:
            ldap_result_id = l.search(base, searchScope,
                                      filterstr, attrlist)
            result_type, result_data = l.result(ldap_result_id, 1)
            return result_data
        except ldap.LDAPError, e:
            logging.error(e.message['desc'])
        finally:
            l and l.unbind_s()
        return None

    #
    # AuthProvider
    #
    def authenticate(self, username, password):

        l = None

        try:
            retrieveAttributes = self._user_attr_map.keys() + \
                [self._login_attr]
            userRDN = self._login_attr + '=' + username
            l = ldap.initialize(self._url)
            l.protocol_version = ldap.VERSION3
            l.simple_bind(userRDN + ',' + self._base, password)
            ldap_result = l.search_s(self._user_base, ldap.SCOPE_SUBTREE,
                                     userRDN, retrieveAttributes)

            bind_dn = ldap_result[0][0]
            l.simple_bind_s(bind_dn, password)

            if ldap_result[0][1]['uid'][0] == username:
                # check if the given username in combination with the LDAP
                # auth method is already in the UserAuthentication table
                user = ldap_result[0][1]
                return {'display': user['givenName'][0],
                        "id": user['uid'][0],
                        "email": user['mail'][0]}
            return None

        except ldap.LDAPError:
            logging.exception("ldap error")
            return None
        except IndexError:
            logging.exception("index error")
            return None
        finally:
            if l:
                l.unbind_s()

    def get_user(self, user_id):
        return self.getUserById(user_id)

    #
    # User Provider
    #
    def getUserById(self, id):
        """
        return the user dictionary in the format of::

            {"id": 123,
            "display": "John Smith",
            "email": "john@example.com"}

        """
        result = self._query(self._user_base,
                             '(%s=%s)' % (self._login_attr, id),
                             self._user_attr_map.keys() + [self._login_attr])

        user = {}

        if not result:
            return None

        for k, v in result[0][1].items():
            user[self._user_attr_map[k]] = v[0]
        return user

    def getUsernameByEmail(self, email):
        if not "@" in email:
            #input is username not email so return username
            return email

        l = None
        try:
            retrieveAttributes = ["uid"]
            l = ldap.initialize(self._url)
            l.protocol_version = ldap.VERSION3
            searchFilter = '(|(mail=%s)(mailalternateaddress=%s))' % (email,
                                                                      email)
            ldap_result = l.search_s(self._user_base, ldap.SCOPE_SUBTREE,
                                     searchFilter, retrieveAttributes)

            logging.debug(ldap_result)
            if ldap_result[0][1]['uid'][0]:
                return ldap_result[0][1]['uid'][0]
            else:
                return None

        except ldap.LDAPError:
            logging.exception("ldap error")
            return None
        except IndexError:
            logging.exception("index error")
            return None
        finally:
            if l:
                l.unbind_s()


def ldap_auth():
    """Return an initialised LDAP backend.
    """

    try:
        base = settings.LDAP_BASE
    except:
        raise ValueError('LDAP_BASE must be specified in settings.py')

    try:
        url = settings.LDAP_URL
    except:
        raise ValueError('LDAP_URL must be specified in settings.py')

    try:
        admin_user = settings.LDAP_ADMIN_USER
    except:
        admin_user = ''

    try:
        admin_password = settings.LDAP_ADMIN_PASSWORD
    except:
        admin_password = ''

    try:
        user_login_attr = settings.LDAP_USER_LOGIN_ATTR
    except:
        raise ValueError('LDAP_USER_LOGIN_ATTR must be specified in settings.py')

    try:
        user_base = settings.LDAP_USER_BASE
    except:
        raise ValueError('LDAP_USER_BASE must be specified in settings.py')

    try:
        user_attr_map = settings.LDAP_USER_ATTR_MAP
    except:
        raise ValueError('LDAP_USER_ATTR_MAP must be specified in settings.py')

    try:
        group_id_attr = settings.LDAP_GROUP_ID_ATTR
    except:
        raise ValueError('LDAP_GROUP_ID_ATTR must be specified in settings.py')

    try:
        group_base = settings.LDAP_GROUP_BASE
    except:
        raise ValueError('LDAP_GROUP_BASE must be specified in settings.py')

    try:
        group_attr_map = settings.LDAP_GROUP_ATTR_MAP
    except:
        raise ValueError('LDAP_GROUP_ATTR_MAP must be specified in settings.py')

    _ldap_auth = LDAPBackend("ldap", url, base, user_login_attr,
                             user_base, user_attr_map, group_id_attr,
                             group_base, group_attr_map, admin_user,
                             admin_password)
    return _ldap_auth
