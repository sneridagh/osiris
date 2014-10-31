from pyramid.interfaces import IAuthenticationPolicy
from pyramid.httpexceptions import HTTPInternalServerError
from osiris.errorhandling import OAuth2ErrorHandler
from osiris.generator import generate_token
from pyramid.settings import asbool


def password_authorization(request, username, password, scope, expires_in, bypass=False):

    ldap_enabled = asbool(request.registry.settings.get('osiris.ldap_enabled'))
    who_enabled = asbool(request.registry.settings.get('osiris.who_enabled'))

    identity = None

    if bypass:
        identity = True
    else:
        if ldap_enabled:
            from osiris import get_ldap_connector
            connector = get_ldap_connector(request)
            identity = connector.authenticate(username, password)

        if who_enabled and not identity:
            policy = request.registry.queryUtility(IAuthenticationPolicy)
            authapi = policy._getAPI(request)
            credentials = {'login': username, 'password': password}

            identity, headers = authapi.login(credentials)

    if not identity:
        return OAuth2ErrorHandler.error_invalid_grant()
    else:
        storage = request.registry.osiris_store
        # Check if an existing token for the username and scope is already issued
        issued = storage.retrieve(username=username, scope=scope)
        if issued:
            # Return the already issued one
            return dict(access_token=issued.get('token'),
                        token_type='bearer',
                        scope=issued.get('scope'),
                        expires_in=issued.get('expire_time')
                        )
        else:
            # Create and store token
            token = generate_token()
            stored = storage.store(token, username, scope, expires_in)

            # Issue token
            if stored:
                return dict(access_token=token,
                            token_type='bearer',
                            scope=scope,
                            expires_in=int(expires_in)
                            )
            else:
                # If operation error, return a generic server error
                return HTTPInternalServerError()
