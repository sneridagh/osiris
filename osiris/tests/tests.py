import unittest
import os

from pyramid import testing
from paste.deploy import loadapp

from osiris.appconst import ACCESS_TOKEN_LENGTH
import json


class osirisTests(unittest.TestCase):
    def setUp(self):
        conf_dir = os.path.dirname(__file__)
        self.app = loadapp('config:test.ini', relative_to=conf_dir)
        from webtest import TestApp
        self.testapp = TestApp(self.app)

    def tearDown(self):
        self.app.registry.osiris_store._conn.drop_collection(self.app.registry.settings.get('osiris.store.collection'))
        testing.tearDown()

    def test_token_endpoint(self):
        # The standard allows arguments with "application/x-www-form-urlencoded"
        testurl = '/token?grant_type=password&username=testuser&password=test'
        resp = self.testapp.post(testurl, status=200)
        response = resp.json
        self.assertTrue('access_token' in response and len(response.get('access_token')) == ACCESS_TOKEN_LENGTH)
        self.assertTrue('token_type' in response and response.get('token_type') == 'bearer')
        self.assertTrue('scope' in response and response.get('scope') is None)
        self.assertTrue('expires_in' in response and response.get('expires_in') == 0)
        self.assertEqual(resp.content_type, 'application/json')

        # Allow pass the arguments via standard post payload
        payload = {"grant_type": "password", "username": "testuser", "password": "test"}
        resp = self.testapp.post('/token', payload, status=200)
        response = resp.json
        self.assertTrue('access_token' in response and len(response.get('access_token')) == ACCESS_TOKEN_LENGTH)
        self.assertTrue('token_type' in response and response.get('token_type') == 'bearer')
        self.assertTrue('scope' in response and response.get('scope') is None)
        self.assertTrue('expires_in' in response and response.get('expires_in') == 0)
        self.assertEqual(resp.content_type, 'application/json')


    def test_token_endpoint_json_payload(self):
        # extension allowing with "application/json"
        testurl = '/token'
        payload = {
            'grant_type': 'password',
            'username': 'testuser',
            'password': 'test'
        }
        resp = self.testapp.post(testurl, json.dumps(payload), status=200, headers={'Content-Type': 'application/json'})
        response = resp.json
        self.assertTrue('access_token' in response and len(response.get('access_token')) == ACCESS_TOKEN_LENGTH)
        self.assertTrue('token_type' in response and response.get('token_type') == 'bearer')
        self.assertTrue('scope' in response and response.get('scope') is None)
        self.assertTrue('expires_in' in response and response.get('expires_in') == 0)
        self.assertEqual(resp.content_type, 'application/json')

        # Allow pass the arguments via standard post payload
        payload = {"grant_type": "password", "username": "testuser", "password": "test"}
        resp = self.testapp.post('/token', payload, status=200)
        response = resp.json
        self.assertTrue('access_token' in response and len(response.get('access_token')) == ACCESS_TOKEN_LENGTH)
        self.assertTrue('token_type' in response and response.get('token_type') == 'bearer')
        self.assertTrue('scope' in response and response.get('scope') is None)
        self.assertTrue('expires_in' in response and response.get('expires_in') == 0)
        self.assertEqual(resp.content_type, 'application/json')

    def test_token_endpoint_empty_password(self):
        # extension allowing with "application/json"
        testurl = '/token'
        payload = {
            'grant_type': 'password',
            'username': 'testuser',
            'scope': 'widgetcli',
            'password': ''
        }
        self.testapp.post(testurl, json.dumps(payload), status=400, headers={'Content-Type': 'application/json'})

    def test_token_with_scope(self):
        # Allow pass the arguments via standard post payload
        payload = {"grant_type": "password", "username": "testuser", "password": "test", "scope": "widgetcli"}
        resp = self.testapp.post('/token', payload, status=200)
        response = resp.json
        self.assertTrue('access_token' in response and len(response.get('access_token')) == ACCESS_TOKEN_LENGTH)
        self.assertTrue('token_type' in response and response.get('token_type') == 'bearer')
        self.assertTrue('scope' in response and response.get('scope') == 'widgetcli')
        self.assertTrue('expires_in' in response and response.get('expires_in') == 0)
        self.assertEqual(resp.content_type, 'application/json')

    def test_token_invalid_or_not_enough_arguments(self):
        # Allow pass the arguments via standard post payload
        payload = {"grant_type": "password", "password": "test"}
        self.testapp.post('/token', payload, status=400)
        payload = {"grant_type": "password", "username": "testuser"}
        self.testapp.post('/token', payload, status=400)

    def test_no_grant_type(self):
        payload = {"username": "testuser", "password": "test"}
        self.testapp.post('/token', payload, status=501)

    def test_not_implemented_grant_type(self):
        payload = {"grant_type": "authorization_code", "username": "testuser", "password": "test"}
        self.testapp.post('/token', payload, status=501)
        payload = {"grant_type": "implicit", "username": "testuser", "password": "test"}
        self.testapp.post('/token', payload, status=501)
        payload = {"grant_type": "client_credentials", "username": "testuser", "password": "test"}
        self.testapp.post('/token', payload, status=501)

    def test_token_endpoint_autherror(self):
        """ On autherrors MUST return Bad Request (400) """
        # Not the password
        testurl = '/token?grant_type=password&username=testuser&password=notthepassword'
        resp = self.testapp.post(testurl, status=400)
        self.assertEqual(resp.content_type, 'application/json')

        # No such user
        testurl = '/token?grant_type=password&username=nosuchuser&password=notthepassword'
        resp = self.testapp.post(testurl, status=400)
        self.assertEqual(resp.content_type, 'application/json')

        # POST payload
        # Not the password
        payload = {"grant_type": "password", "username": "testuser", "password": "notthepassword"}
        resp = self.testapp.post('/token', payload, status=400)
        self.assertEqual(resp.content_type, 'application/json')

        # POST payload
        # No such user
        payload = {"grant_type": "password", "username": "nosuchuser", "password": "notthepassword"}
        resp = self.testapp.post('/token', payload, status=400)
        self.assertEqual(resp.content_type, 'application/json')

    def test_token_storage(self):
        testurl = '/token?grant_type=password&username=testuser&password=test'
        resp = self.testapp.post(testurl, status=200)
        response = resp.json

        token_store = self.app.registry.osiris_store.retrieve(token=response.get('access_token'))
        self.assertTrue(token_store)
        self.assertEqual(token_store.get('token'), response.get('access_token'))
        self.assertEqual(token_store.get('username'), 'testuser')

    def test_check_token_endpoint(self):
        testurl = '/token?grant_type=password&username=testuser&password=test'
        resp = self.testapp.post(testurl, status=200)
        response = resp.json
        access_token = response.get('access_token')

        testurl = '/checktoken?access_token=%s&username=testuser' % (str(access_token))
        self.testapp.post(testurl, status=200)

        # POST payload
        payload = {"access_token": str(access_token), "username": "testuser"}
        resp = self.testapp.post('/checktoken', payload, status=200)

    def test_check_token_endpoint_json_payload(self):
        testurl = '/token?grant_type=password&username=testuser&password=test'
        resp = self.testapp.post(testurl, status=200)
        response = resp.json
        access_token = response.get('access_token')

        testurl = '/checktoken'
        payload = {
            'access_token': access_token,
            'username': 'testuser',
        }
        resp = self.testapp.post(testurl, json.dumps(payload), status=200, headers={'Content-Type': 'application/json'})

        testurl = '/checktoken?access_token=%s&username=testuser' % (str(access_token))
        self.testapp.post(testurl, status=200)

        # POST payload
        payload = {"access_token": str(access_token), "username": "testuser"}
        resp = self.testapp.post('/checktoken', payload, status=200)

    def test_check_token_endpoint_with_scope(self):
        testurl = '/token?grant_type=password&username=testuser&password=test&scope=widgetcli'
        resp = self.testapp.post(testurl, status=200)
        response = resp.json
        access_token = response.get('access_token')

        testurl = '/checktoken?access_token=%s&username=testuser&scope=widgetcli' % (str(access_token))
        self.testapp.post(testurl, status=200)

        # POST payload
        payload = {"access_token": str(access_token), "username": "testuser", "scope": "widgetcli"}
        resp = self.testapp.post('/checktoken', payload, status=200)

    def test_check_token_endpoint_autherror(self):
        testurl = '/token?grant_type=password&username=testuser&password=test'
        resp = self.testapp.post(testurl, status=200)
        response = resp.json
        access_token = response.get('access_token')

        testurl = '/checktoken?access_token=%s&username=testuser2' % (str(access_token))
        self.testapp.post(testurl, status=401)

        # POST payload
        payload = {"access_token": str(access_token), "username": "testuser2"}
        resp = self.testapp.post('/checktoken', payload, status=401)

    def test_check_token_endpoint_guessed_token(self):
        # POST payload
        payload = {"access_token": "qwe1235rwersdgasdfghjkyuiyuihfgh", "username": "testuser2"}
        self.testapp.post('/checktoken', payload, status=401)

    def test_check_token_not_enough_arguments(self):
        # POST payload
        payload = {"username": "testuser2"}
        self.testapp.post('/checktoken', payload, status=400)
        payload = {"access_token": "qwe1235rwersdgasdfghjkyuiyuihfgh"}
        self.testapp.post('/checktoken', payload, status=400)

    def test_check_token_lenght_not_valid(self):
        # POST payload
        payload = {"access_token": "qwe1235rrsdgasdfghjkyuiyuihfgh", "username": "testuser2"}
        self.testapp.post('/checktoken', payload, status=400)

    def test_grant_same_token(self):
        testurl = '/token?grant_type=password&username=testuser&password=test'
        resp = self.testapp.post(testurl, status=200)
        response = resp.json
        access_token = response.get('access_token')

        testurl = '/token?grant_type=password&username=testuser&password=test'
        resp = self.testapp.post(testurl, status=200)
        response = resp.json
        self.assertEqual(access_token, response.get('access_token'))

    def test_bypass_token_endpoint(self):
        # The standard allows arguments with "application/x-www-form-urlencoded"
        testurl = '/token-bypass?grant_type=password&username=testuser&password='
        resp = self.testapp.post(testurl, status=200)
        response = resp.json
        self.assertTrue('access_token' in response and len(response.get('access_token')) == ACCESS_TOKEN_LENGTH)
        self.assertTrue('token_type' in response and response.get('token_type') == 'bearer')
        self.assertTrue('scope' in response and response.get('scope') is None)
        self.assertTrue('expires_in' in response and response.get('expires_in') == 0)
        self.assertEqual(resp.content_type, 'application/json')

        # Allow pass the arguments via standard post payload
        payload = {"grant_type": "password", "username": "testuser"}
        resp = self.testapp.post('/token-bypass', payload, status=200)
        response = resp.json
        self.assertTrue('access_token' in response and len(response.get('access_token')) == ACCESS_TOKEN_LENGTH)
        self.assertTrue('token_type' in response and response.get('token_type') == 'bearer')
        self.assertTrue('scope' in response and response.get('scope') is None)
        self.assertTrue('expires_in' in response and response.get('expires_in') == 0)
        self.assertEqual(resp.content_type, 'application/json')
