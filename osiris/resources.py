from osiris.generators import generate_token
from random import choice


ACCESS_TOKEN_LENGTH = 10
REFRESH_TOKEN_LENGTH = 10
CLIENT_KEY_LENGTH = 8
CLIENT_SECRET_LENGTH = 20
ALLOWED_CHARACTERS = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ0123456789'


class Root(object):
    def __init__(self, request):
        self.request = request


def issue_token(request, username, password, scope):

    token = oAuth2AccessToken()


class oAuth2AccessToken(object):
    """Wrapper of the token collection objects"""

    collection = 'tokens'

    schema = [
                'username',
                'token',
                'scope',
                'issued_at',
                'expires_at',
                'revoked_at'
            ]

    def __init__(self, token=None):
        if token is not None:
            self.generate_token()

    def generate_token(self, length=ACCESS_TOKEN_LENGTH, allowed_chars=ALLOWED_CHARACTERS):
        # We assume that the token will be enough random, otherwise we need to make sure of it
        return ''.join([choice(allowed_chars) for i in range(length)])
