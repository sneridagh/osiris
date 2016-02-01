from pyramid.httpexceptions import HTTPInternalServerError
from osiris.errorhandling import OAuth2ErrorHandler
import jwt
from osiris.connector import get_connector
from datetime import datetime, timedelta


def password_authorization(request, username, password, scope, bypass=False):

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
                    expires=issued.get('expire_time')
                    )
    else:
        token_duration = int(request.registry.settings.get('osiris.jwt.expiry', 0))
        token_secret = request.registry.settings.get('osiris.jwt.secret', 'secret')
        token_algorithm = request.registry.settings.get('osiris.jwt.algorithm', 'HS256')
        # Create and store token
        token_payload = (
            {
                'sub': username,
            }
        )
        if token_duration > 0:
            token_expiration_time = (datetime.utcnow() + timedelta(seconds=token_duration))
            token_expiration_timestamp = token_expiration_time.strftime('%s')
            token_payload['exp'] = token_expiration_timestamp
        else:
            token_expiration_time = None
            token_expiration_timestamp = None

        token = jwt.encode(token_payload, token_secret, algorithm=token_algorithm)
        stored = storage.store(token, username, scope, token_expiration_time)

        # Issue token
        if stored:
            return dict(access_token=token,
                        token_type='bearer',
                        scope=scope,
                        expires=token_expiration_timestamp
                        )
        else:
            # If operation error, return a generic server error
            return HTTPInternalServerError()
