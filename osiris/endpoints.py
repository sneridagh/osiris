from pyramid.view import view_config
from pyramid.httpexceptions import HTTPOk, HTTPUnauthorized, HTTPNoContent
from pyramid.response import Response
from osiris.appconst import ACCESS_TOKEN_REGEX
from osiris.errorhandling import OAuth2ErrorHandler
from osiris.authorization import password_authorization

import re


def extract_params(request):
    if request.content_type == 'application/json':
        params = request.json
    else:
        params = request.params
    return params


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
    params = extract_params(request)

    grant_type = params.get('grant_type')

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
        scope = params.get('scope', None)  # Optional
        username = params.get('username', None)
        password = params.get('password', None)
        if username is None:
            return OAuth2ErrorHandler.error_invalid_request('Required parameter username not found in the request')
        elif password is None:
            return OAuth2ErrorHandler.error_invalid_request('Required parameter password not found in the request')
        else:
            return password_authorization(request, username, password, scope)
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
    params = extract_params(request)
    access_token = params.get('access_token')
    username = params.get('username')
    scope = params.get('scope', None)

    if username is None:
        return OAuth2ErrorHandler.error_invalid_request('Required parameter username not found in the request')
    elif access_token is None:
        return OAuth2ErrorHandler.error_invalid_request('Required parameter access_token not found in the request')
    elif re.match(ACCESS_TOKEN_REGEX, access_token, re.IGNORECASE) is None:
        return OAuth2ErrorHandler.error_invalid_request('Required parameter not valid found in the request')

    storage = request.registry.osiris_store
    token_info = storage.retrieve(token=access_token)
    if token_info:
        if token_info.get('scope') == scope and token_info.get('username') == username:
            return HTTPOk()
        else:
            return HTTPUnauthorized()

    return HTTPUnauthorized()


@view_config(name='token-bypass',
             renderer='json',
             request_method='POST',
             http_cache=0)
def bypass_token_endpoint(request):
    """
    Anonymous version of the osiris.token_endpoint. This endpoint differs from
    the original in that the password is not required and the password_authorization
    is done bypassing authentication.

    NOTE:This endpoint MUST be firewalled.
    """
    expires_in = request.registry.settings.get('osiris.tokenexpiry', 0)
    params = extract_params(request)

    grant_type = params.get('grant_type')

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
        scope = params.get('scope', None)  # Optional
        username = params.get('username', None)
        if username is None:
            return OAuth2ErrorHandler.error_invalid_request('Required parameter username not found in the request')
        username = username.strip(' ')
        if username is '':
            return OAuth2ErrorHandler.error_invalid_request('Required parameter cannot be empty')

        return password_authorization(request, username, None, scope, expires_in, bypass=True)
    else:
        return OAuth2ErrorHandler.error_unsupported_grant_type()


@view_config(name='revoke',
             renderer='json',
             request_method='POST',
             http_cache=0)
def revoke_token_endpoint(request):
    params = extract_params(request)
    access_token = params.get('access_token')
    username = params.get('username')

    if username is None:
        return OAuth2ErrorHandler.error_invalid_request('Required parameter username not found in the request')
    elif access_token is None:
        return OAuth2ErrorHandler.error_invalid_request('Required parameter access_token not found in the request')
    elif len(access_token) != ACCESS_TOKEN_LENGTH:
        return OAuth2ErrorHandler.error_invalid_request('Required parameter not valid found in the request')

    storage = request.registry.osiris_store
    deleted = storage.delete(token=access_token)
    if deleted:
        return HTTPNoContent()
    else:
        return HTTPUnauthorized()

    return HTTPUnauthorized()
