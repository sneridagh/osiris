from pyramid.httpexceptions import HTTPInternalServerError
from osiris.errorhandling import OAuth2ErrorHandler
from osiris.generator import generate_token
from osiris.connector import get_connector


def password_authorization(request, username, password, scope, expires_in, bypass=False):

    connector = get_connector(request)
    error_description = ''

    # Bypass authentication only if the user exists on the connector
    if bypass:
        if connector.user_exists(username):
            identity = True
        else:
            error_description = 'No such user "{}"'.format(username)
            identity = None

    # Without bypass perform regular authentication
    else:
        identity = connector.check_credentials(username, password)

    # Return an error on missing identity
    if not identity:
        return OAuth2ErrorHandler.error_invalid_grant(description=error_description)

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
