import unittest

from pyramid import testing
from pyramid.testing import DummyRequest

import pymongo
import json
from bson import json_util


class DummyRequestREST(DummyRequest):
    """ Enriching the DummyRequest to have more properties """
    def __init__(self, params=None, environ=None, headers=None, path='/',
                 cookies=None, post=None, **kw):
        super(DummyRequestREST, self).__init__(params=params, environ=environ, headers=headers, path=path,
                 cookies=cookies, post=post, **kw)

        self.content_type = ""

testSettings = {'mongodb.url': 'mongodb://localhost', 'mongodb.db_name': 'testDB'}


class osirisTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_token_endpoint(self):
        pass

    # def test_my_view(self):
    #     from osiris.views import my_view
    #     request = testing.DummyRequest()
    #     info = my_view(request)
    #     self.assertEqual(info['project'], 'osiris')
