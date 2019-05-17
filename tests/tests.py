import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

import unittest
from main import app


class LoadHomeTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_route_slash(self):
        res = self.app.get("/")
        assert res.status_code == 200
        assert b"fill up the form" in res.data

    def test_route_index(self):
        res = self.app.get("/index")
        assert res.status_code == 200
        assert b"fill up the form" in res.data

    def test_route_random(self):
        res = self.app.get("/random")
        assert res.status_code == 404
