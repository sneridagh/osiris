from pyramid.httpexceptions import HTTPUnauthorized, HTTPBadRequest, HTTPNotImplemented
from pyramid.response import Response

import json


class JSONHTTPUnauthorized(HTTPUnauthorized):

    def __init__(self, error):
        Response.__init__(self, json.dumps(error), status=self.code)
        self.content_type = 'application/json'


class JSONHTTPBadRequest(HTTPBadRequest):

    def __init__(self, error):
        Response.__init__(self, json.dumps(error), status=self.code)
        self.content_type = 'application/json'


class JSONHTTPNotImplemented(HTTPNotImplemented):

    def __init__(self, error):
        Response.__init__(self, json.dumps(error), status=self.code)
        self.content_type = 'application/json'


class OAuth2ErrorHandler(object):

    @staticmethod
    def error_invalid_request(error_description=""):
        """
        The request is missing a required parameter, includes an
        unsupported parameter or parameter value, repeats a
        parameter, includes multiple credentials, utilizes more
        than one mechanism for authenticating the client, or is
        otherwise malformed.
        """
        return dict(error='invalid_request',
                    error_description=error_description)

    @staticmethod
    def error_invalid_client():
        """
        Client authentication failed (e.g. unknown client, no
        client authentication included, multiple client
        authentications included, or unsupported authentication
        method). The authorization server MAY return an HTTP 401
        (Unauthorized) status code to indicate which HTTP
        authentication schemes are supported. If the client
        attempted to authenticate via the "Authorization" request
        header field, the authorization server MUST respond with
        an HTTP 401 (Unauthorized) status code, and include the
        "WWW-Authenticate" response header field matching the
        authentication scheme used by the client.
        """
        return dict(error='invalid_client',
                    error_description="")

    @staticmethod
    def error_invalid_grant():
        """
        The provided authorization grant is invalid, expired,
        revoked, does not match the redirection URI used in the
        authorization request, or was issued to another client.
        """
        return dict(error='invalid_grant',
                    error_description="")

    @staticmethod
    def error_unauthorized_client():
        """
        The authenticated user is not authorized to use this
        authorization grant type.
        """
        error_response = dict(error='unauthorized_client',
                              error_description="")

        return JSONHTTPUnauthorized(error_response)

    @staticmethod
    def error_unsupported_grant_type():
        """
        The authorization grant type is not supported by the
        authorization server.
        """
        error_response = dict(error='unsupported_grant_type',
                              error_description="")

        return JSONHTTPNotImplemented(error_response)

    @staticmethod
    def error_invalid_scope():
        """
        The requested scope is invalid, unknown, malformed, or
        exceeds the scope granted by the resource owner.
        """
        return dict(error='invalid_scope',
                    error_description="")

    @staticmethod
    def error_invalid_token(token_type):
        """
        The specific handling of this error is based on the token
        type used, i.e. bearer or MAC.
        """
        raise HTTPUnauthorized('todo') # TODO: add correct error handling for bearer
