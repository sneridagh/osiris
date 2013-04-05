from pyramid.interfaces import IAuthenticationPolicy
from pyramid.httpexceptions import HTTPInternalServerError
from osiris.errorhandling import OAuth2ErrorHandler
from osiris.generator import generate_token


def password_authorization(request, username, password, scope, expires_in):

    ldap_enabled = request.registry.settings.get('osiris.ldap_enabled')

    if ldap_enabled:
        from osiris import get_ldap_connector
        connector = get_ldap_connector(request)
        identity = connector.authenticate(username, password)

    else:
        policy = request.registry.queryUtility(IAuthenticationPolicy)
        authapi = policy._getAPI(request)
        credentials = {'login': username, 'password': password}

        identity, headers = authapi.login(credentials)

    if not identity:
        return OAuth2ErrorHandler.error_unauthorized_client()
    else:
        # Create and store token
        storage = request.registry.osiris_store
        token = generate_token()
        stored = storage.store(token, username, scope, expires_in)

        # Issue token
        if stored:
            return dict(access_token=token,
                        token_type='bearer',
                        scope=scope,
                        expires_in=expires_in
                        )
        else:
            # If operation error, return a generic server error
            return HTTPInternalServerError()
