import unittest
import os
from pyramid import testing
from paste.deploy import loadapp


class osirisTests(unittest.TestCase):
    def setUp(self):
        conf_dir = os.path.abspath(__file__ + '/../..')
        app = loadapp('config:development.ini', relative_to=conf_dir)
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        testing.tearDown()

    def test_token_endpoint(self):
        res = self.testapp.post('/token?grant_type=password&username=victor&password=1', status=200)


    # def test_my_view(self):
    #     from osiris.views import my_view
    #     request = testing.DummyRequest()
    #     info = my_view(request)
    #     self.assertEqual(info['project'], 'osiris')
