import unittest
from pyramid import testing

from osiris.appconst import ACCESS_TOKEN_LENGTH

LEGACY_URL = 'https://oauth.upc.edu'


class legacyTests(unittest.TestCase):
    def setUp(self):
        from webtest import TestApp
        self.testapp = TestApp(LEGACY_URL)

    def tearDown(self):
        testing.tearDown()

    # def test_issue_token(self):
    #     # Legacy does not allows arguments with "application/x-www-form-urlencoded"
    #     testurl = '/token?grant_type=password&username=usuari.iescude&password=holahola&client_id=MAX'
    #     self.testapp.post(testurl, status=400)

    #     # However it allows only via POST payload
    #     payload = {"grant_type": "password", "username": "usuari.iescude", "password": "holahola", "client_id": "MAX"}
    #     resp = self.testapp.post('/token', payload)
    #     import ipdb;ipdb.set_trace()
    #     response = resp.json
    #     # Responds with oauth_token instead of the standard access_token
    #     self.assertTrue('oauth_token' in response and len(response.get('oauth_token')) == ACCESS_TOKEN_LENGTH)
    #     # No token_type
    #     # self.assertTrue('token_type' in response and response.get('token_type') == 'bearer')
    #     # If no scope is defined, the response is None
    #     self.assertTrue('scope' in response and response.get('scope') is None)
    #     # No expires_in
    #     # self.assertTrue('expires_in' in response and response.get('expires_in') == 0)
    #     self.assertEqual(resp.content_type, 'application/json')

    def test_issue_token_invalid_credentials(self):
        # Legacy does not allows arguments with "application/x-www-form-urlencoded"
        testurl = '/token?grant_type=password&username=usuari.iescude2&password=holahola&client_id=MAX'
        self.testapp.post(testurl, status=400)

        # However it allows only via POST payload
        payload = {"grant_type": "password", "username": "usuari.iescude2", "password": "holahola", "client_id": "MAX"}
        self.testapp.post('/token', payload, status=400)

    # def test_check_token_endpoint(self):
    #     payload = {"grant_type": "password", "username": "usuari.iescude", "password": "holahola", "client_id": "MAX"}
    #     resp = self.testapp.post('/token', payload, status=200)
    #     response = resp.json
    #     access_token = response.get('oauth_token')

    #     # Legacy does not allows arguments with "application/x-www-form-urlencoded"
    #     testurl = '/checktoken?oauth_token=%s&user_id=usuari.iescude' % (str(access_token))
    #     # Response 401 no body (!)
    #     self.testapp.post(testurl, status=401)

    #     # However it allows only via POST payload
    #     # uses oauth_token instead of access_token and user_id instead of username
    #     payload = {"oauth_token": str(access_token), "user_id": "usuari.iescude"}
    #     # Response 200 no body
    #     resp = self.testapp.post('/checktoken', payload, status=200)
