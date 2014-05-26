from pyramid.view import view_config
from pyramid.httpexceptions import HTTPOk, HTTPUnauthorized
from pyramid.response import Response
from osiris.appconst import ACCESS_TOKEN_LENGTH
from osiris.errorhandling import OAuth2ErrorHandler
from osiris.authorization import password_authorization


@view_config(route_name='default_view',
             request_method='GET',
             http_cache=0)
def default_view(request):
    return Response("I am an Osiris")


@view_config(name='token',
             renderer='json',
             request_method='POST',
             http_cache=0)
def token_endpoint(request):
    """
    The token endpoint is used by the client to obtain an access token by
    presenting its authorization grant or refresh token. The token
    endpoint is used with every authorization grant except for the
    implicit grant type (since an access token is issued directly).
    """
    expires_in = request.registry.settings.get('osiris.tokenexpiry', 0)

    grant_type = request.params.get('grant_type')

    # Authorization Code Grant
    if grant_type == 'authorization_code':
        return OAuth2ErrorHandler.error_unsupported_grant_type()
    # Implicit Grant
    elif grant_type == 'implicit':
        return OAuth2ErrorHandler.error_unsupported_grant_type()
    # Client Credentials
    elif grant_type == 'client_credentials':
        return OAuth2ErrorHandler.error_unsupported_grant_type()
    # Client Credentials Grant
    elif grant_type == 'password':
        scope = request.params.get('scope', None)  # Optional
        username = request.params.get('username', None)
        password = request.params.get('password', None)
        if username is None:
            return OAuth2ErrorHandler.error_invalid_request('Required parameter username not found in the request')
        elif password is None:
            return OAuth2ErrorHandler.error_invalid_request('Required parameter password not found in the request')
        else:
            return password_authorization(request, username, password, scope, expires_in)
    else:
        return OAuth2ErrorHandler.error_unsupported_grant_type()


@view_config(name='checktoken',
             renderer='json',
             request_method='POST',
             http_cache=0)
def check_token_endpoint(request):
    """
    This endpoint is out of the oAuth 2.0 specification, however it's needed in
    order to support total desacoplation of the oAuth server and the resource
    servers. When an application (a.k.a. client) impersons the user in order to
    access to the user's resources, the resource server needs to check if the
    token provided is valid and check if it was issued to the user.
    """

    access_token = request.params.get('access_token')
    username = request.params.get('username')
    scope = request.params.get('scope', None)

    if username is None:
        return OAuth2ErrorHandler.error_invalid_request('Required parameter username not found in the request')
    elif access_token is None:
        return OAuth2ErrorHandler.error_invalid_request('Required parameter access_token not found in the request')
    elif len(access_token) != ACCESS_TOKEN_LENGTH:
        return OAuth2ErrorHandler.error_invalid_request('Required parameter not valid found in the request')

    storage = request.registry.osiris_store
    token_info = storage.retrieve(token=access_token)
    if token_info:
        if token_info.get('scope') == scope and token_info.get('username') == username:
            return HTTPOk()
        else:
            return HTTPUnauthorized()

    return HTTPUnauthorized()
