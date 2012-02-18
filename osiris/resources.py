from osiris.mdbhelpers import MDBObject
from random import choice
import datetime

ACCESS_TOKEN_LENGTH = 20
REFRESH_TOKEN_LENGTH = 10
CLIENT_KEY_LENGTH = 8
CLIENT_SECRET_LENGTH = 20
ALLOWED_CHARACTERS = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ0123456789'


class Root(object):
    def __init__(self, request):
        self.request = request


def normalize_for_response(token, expires_in):
    return dict(
                token=token['token'],
                scope=token['scope'],
                expires_in=expires_in
                )


def issue_token(request, username, scope, expires_in=3600):

    data = {"username": username,
            "scope": scope,
            "expires_in": expires_in}

    token = oAuth2AccessToken(data)
    request.db[token.collection].insert(token)
    # import ipdb; ipdb.set_trace( )
    return normalize_for_response(token, expires_in)


class oAuth2AccessToken(MDBObject):
    """An oAuthAccessToken Object"""

    collection = 'tokens'

    data = {}
    schema = {
                '_id': dict(required=0),
                'username': dict(required=0, request=1),
                'scope': dict(required=0, request=1),
                'token': dict(required=0),
                'issued_at': dict(required=0),
                'expires_at': dict(required=0),
                'revoked_at': dict(required=0),
             }

    def __init__(self, data):
        """
        """
        self.data = data
        self.validate()

        if self.data.get('token', None) is None:
            self.data['token'] = self.generate_token()

        self.data['issued_at'] = datetime.datetime.now()

        if self.data.get('expires_in') == 0:
            self.data['expires_at'] = 0
        else:
            timedelta = datetime.timedelta(seconds=int(self.data.get('expires_in')))
            self.data['expires_at'] = self.data.get('issued_at') + timedelta

        self.update(data)

    def generate_token(self, length=ACCESS_TOKEN_LENGTH, allowed_chars=ALLOWED_CHARACTERS):
        # We assume that the token will be enough random, otherwise we need
        # to make sure the generated token doesn't exists previously in DB
        return ''.join([choice(allowed_chars) for i in range(length)])
