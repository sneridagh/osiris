# -*- coding: utf-8 -*-
from osiris.errorhandling import OAuth2ErrorHandler
from ldap import SCOPE_SUBTREE
from ldap import NO_SUCH_OBJECT
from pyramid.settings import asbool
from pyramid.interfaces import IAuthenticationPolicy

from functools import partial


class OsirisConnector(object):
    """
        Base class to abstract an authentication system
    """

    def __init__(self, request):
        self.request = request

    def user_exists(self, userid):
        """
            Returns a boolean indicating wether the user exists on
            this connector.

            If not implemented by subclasses will assume that user
            exists.
        """
        return True

    def check_credentials(self, userid, credentials):
        """
            Returns a boolean indicating wether the provided
            userid and credentials are valid on this connnector
        """
        pass

    def normalize_username(self, username):
        """
            Normalizes the username to lower case by default.
        """
        return username.lower()


class LdapConnector(OsirisConnector):

    def __init__(self, *args, **kwargs):
        OsirisConnector.__init__(self, *args, **kwargs)

        # Leave this import here, as it won't be available if
        # package is installed without [ldap] support
        from osiris import get_ldap_connector
        self.ldap = get_ldap_connector(self.request)

    def user_exists(self, username):
        """
            Search for a user cn on all tree under base_dn.
        """
        userid = self.normalize_username(username)
        with self.ldap.manager.connection(self.ldap.manager.bind, self.ldap.manager.passwd) as conn:
            search_id = conn.search(
                self.request.registry.ldap_login_query.base_dn,
                SCOPE_SUBTREE,
                'cn={userid}'.format(userid=userid))
            try:
                result = conn.result(search_id)
            except NO_SUCH_OBJECT:
                # Only raised when base_dn don't exists
                return False
            else:
                # Check if there's any matches.
                return len(result[1]) > 0

    def check_credentials(self, username, password):
        userid = self.normalize_username(username)
        return self.ldap.authenticate(userid, password)


class WhoConnector(OsirisConnector):
    def __init__(self, *args, **kwargs):
        OsirisConnector.__init__(self, *args, **kwargs)

        policy = self.request.registry.queryUtility(IAuthenticationPolicy)
        self.who = policy._getAPI(self.request)

    def check_credentials(self, username, password):
        userid = self.normalize_username(username)
        identity, headers = self.who.login({'login': userid, 'password': password})
        return identity


class MultiConnector(object):
    """
        Encapsulates method access to multiple connectors, seen as only one conector
        from the outside world. For each method accessed, iterates trough all connector
        methods in order
    """
    def __init__(self, connectors):
        self.connectors = connectors

    def _conector_iterator_(self, method_name, *args, **kwargs):
        """
            Executes method on all defined connectors until a truish value
            is found, otherwise returns None.
        """
        for connector in self.connectors:
            method = getattr(connector, method_name)
            result = method(*args, **kwargs)
            if result:
                return result

    def __getattr__(self, method):
        """
            Returns _conector_iterator_ method instance with the method
            parameter set.
        """
        return partial(self._conector_iterator_, method)


def get_connector(request):
    ldap_enabled = asbool(request.registry.settings.get('osiris.ldap_enabled'))
    who_enabled = asbool(request.registry.settings.get('osiris.who_enabled'))

    connectors = []
    if who_enabled:
        connectors.append(WhoConnector(request))
    if ldap_enabled:
        connectors.append(LdapConnector(request))
    if not connectors:
        return None

    return MultiConnector(connectors)
