import unittest
import os
from pyramid import testing
from paste.deploy import loadapp


class osirisTests(unittest.TestCase):
    def setUp(self):
        conf_dir = os.path.dirname(__file__)
        self.app = loadapp('config:test.ini', relative_to=conf_dir)
        from webtest import TestApp
        self.testapp = TestApp(self.app)

    def tearDown(self):
        # self.app.registry.osiris_store._conn.drop_collection(self.app.registry.settings.get('osiris.store.collection'))
        testing.tearDown()

    def test_token_endpoint(self):
        testurl = '/token?grant_type=password&username=testuser&password=test'
        resp = self.testapp.post(testurl, status=200)
        response = resp.json
        self.assertTrue('access_token' in response and len(response.get('access_token')) == 20)
        self.assertTrue('token_type' in response and response.get('token_type') == 'bearer')
        self.assertTrue('scope' in response and response.get('scope') == '')
        self.assertTrue('expires_in' in response and response.get('expires_in') == '0')
        self.assertEqual(resp.content_type, 'application/json')

    def test_token_endpoint_autherror(self):
        # Not the password
        testurl = '/token?grant_type=password&username=testuser&password=notthepassword'
        resp = self.testapp.post(testurl, status=401)
        self.assertEqual(resp.content_type, 'application/json')

        # No such user
        testurl = '/token?grant_type=password&username=nosuchuser&password=notthepassword'
        resp = self.testapp.post(testurl, status=401)
        self.assertEqual(resp.content_type, 'application/json')

    def test_token_storage(self):
        testurl = '/token?grant_type=password&username=testuser&password=test'
        resp = self.testapp.post(testurl, status=200)
        response = resp.json

        token_store = self.app.registry.osiris_store.retrieve(response.get('access_token'))
        self.assertTrue(token_store)
        self.assertEqual(token_store.get('token'), response.get('access_token'))
        self.assertEqual(token_store.get('username'), 'testuser')
