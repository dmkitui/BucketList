import unittest
from base import BaseBucketListCase
import json


class BucketList_DB(BaseBucketListCase):
    '''The bucketlist base tests'''

    def test_bucketlist_access_not_allowed(self):
        '''Tests access to bucketlist not allowed to users not logged in'''
        response = self.client().get('/api/v1/bucketlists/')
        self.assertEqual(response.status_code, 401)

        response2 = self.client().post('/api/v1/bucketlists/')
        self.assertEqual(response2.status_code, 401)


    def test_bucketlist_create_list_item(self):
        '''Test it can create a bucketlist post request'''

        self.user_registration('dan@example.org', 'StrongPwd76', 'StrongPwd76')
        response, status_code = self.user_login('dan@example.org', 'StrongPwd76')

        token = response['access_token']

        response = self.client().post('/api/v1/bucketlists/', headers=dict(Authorization="Bearer " + token), data=dict(name='Learn Programming'))

        data = json.loads(response.data.decode())

        self.assertTrue(data['name'] == 'Learn Programming')
        self.assertEqual(response.status_code, 201)

    def test_get_all_bucketlists(self):
        '''Tests it can get all bucketlist'''
        self.user_registration('dan@example.org', 'StrongPwd76', 'StrongPwd76')

        response, status_code = self.user_login('dan@example.org', 'StrongPwd76')
        token = response['access_token']

        response2 = self.client().post('/api/v1/bucketlists/', headers=dict(Authorization="Bearer " + token), data=dict(name='Learn Programming'))
        self.assertEqual(response2.status_code, 201)

        response3 = self.client().get('/api/v1/bucketlists/', headers=dict(Authorization="Bearer " + token))

        self.assertTrue(response3.status_code == 200)
        self.assertIn('Learn Programming', str(response3.data))

    def test_bucketlist_delete_list_item(self):
        '''Test it can delete an existing bucketlist item'''
        pass

    def test_bucketlist_edit_list_item(self):
        '''Test it can edit an existing list item.'''
        pass

    def test_bucketlist_return_all(self):
        '''Test it can return all exisiting bucketlist items'''
        pass

    def test_bucketlist_get_list_item_by_id(self):
        '''Test it can return a list item by id'''
        pass

    def test_bucketlist_search_by_name(self):
        '''Test bucketlist items can be searched by name'''
        pass

    def test_bucketlist_pagination(self):
        '''Test the response is formatted by the requested page size'''
        pass

    def test_bucketlist_authetication_unauthenticated_user(self):
        '''Test that a user who is not logged in can only login and register'''
        pass

    def test_bucketlist_authetication_authenticated_user(self):
        '''Test a logged-in user can post bucketlists, update  the list items and search'''

if __name__ == '__main__':
    unittest.main()