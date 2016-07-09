import json
import logging
import unittest

import webapp
import re

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class UsersTestCase(unittest.TestCase):
    def setUp(self):
        self.app = webapp.app.test_client()
        rv = self.app.get('/login', follow_redirects=True)
        mo = re.search(r'name="csrf_token" type="hidden" value="([0-9]+##[0-9a-f]+)"', rv.data)
        token = mo.group(1)
        rv = self.app.post('/login',
                           follow_redirects=True,
                           data={'csrf_token': token,
                                 'email': 'admin',
                                 'password': 'password'})

    def tearDown(self):
        pass

    def test_list_users(self):
        rv = self.app.get('/api/users')
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data
        self.assertIsInstance(data, list)
        admin_data = [row for row in data if row['id'] == 1][0]['values']
        self.assertEqual(admin_data['email'], 'admin')
        self.assertTrue(admin_data['admin'])

    def test_add_delete_user(self):
        data = {'user-email': 'test-user',
                'user-active': False,
                'user-admin': False,
                'user-pass1': 'test-pass'}
        rv = self.app.post('/api/users',
                           data=data)
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        uid = result['data']
        print uid

        rv = self.app.delete('/api/users/%s' % uid)
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)

    def test_modify_user(self):
        data = {'user-email': 'test-user2',
                'user-active': False,
                'user-admin': False,
                'user-pass1': 'test-pass'}
        rv = self.app.post('/api/users',
                           data=data)
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        uid = result['data']
        print uid

        update = {'key': 'email',
                  'value': 'renamed-test-user2'}
        rv = self.app.put('/api/users/%s' % uid,
                           data=update)
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)

        rv = self.app.get('/api/users')
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data
        self.assertIsInstance(data, list)
        test_user_data = [row for row in data if row['id'] == uid][0]['values']
        self.assertEqual(test_user_data['email'], 'renamed-test-user2')

        rv = self.app.delete('/api/users/%s' % uid)
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)


if __name__ == '__main__':
    unittest.main()
