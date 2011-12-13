from pyramid.interfaces import IAuthenticationPolicy
from osiris.errorhandling import OAuth2ErrorHandler
from osiris.resources import issue_token


def password_authorization(request, username, password, scope):

    policy = request.registry.queryUtility(IAuthenticationPolicy)
    authapi = policy._getAPI(request)
    credentials = {'login': username, 'password': password}

    identity, headers = authapi.login(credentials)

    if not identity:
        return OAuth2ErrorHandler.error_unauthorized_user()
    else:
        issue_token(request, username, password, scope)
