# coding=utf-8
import json
import unittest

from flask import jsonify

import numpy as np
import webapp


class JsonTestCase(unittest.TestCase):
    def setUp(self):
        self.app = webapp.app.test_client()

    def tearDown(self):
        pass

    def test_encode_nan(self):
        a = [np.nan]
        with webapp.app.test_request_context():
            s = jsonify(a)
            r = json.loads(s.data)
            self.assertListEqual(r, [None])


if __name__ == '__main__':
    unittest.main()
