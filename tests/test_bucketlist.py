import unittest
import json

# from base import BaseBucketListCase
from . import base

class BucketList_DB(base.BaseBucketListCase):
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


    def test_get_non_existent_bucekt_list(self):
        '''test get on a non-existent-bucketlist'''
        self.user_registration('dan@example.org', 'StrongPwd76', 'StrongPwd76')

        response, status_code = self.user_login('dan@example.org', 'StrongPwd76')
        token = response['access_token']

        response2 = self.client().get('/api/v1/bucketlists/101', headers=dict(Authorization="Bearer " + token))

        self.assertTrue(response2.status_code == 404)
        self.assertIn('That bucketlist item does not exist', str(response2.data))


    def test_get_no_bucket_list_available(self):
        '''test get on a non-existent-bucketlist'''
        self.user_registration('dan@example.org', 'StrongPwd76', 'StrongPwd76')

        response, status_code = self.user_login('dan@example.org', 'StrongPwd76')
        token = response['access_token']

        response2 = self.client().get('/api/v1/bucketlists/', headers=dict(Authorization="Bearer " + token))
        print(response2.data)

        self.assertTrue(response2.status_code == 200)
        self.assertIn('No bucketlists available', str(response2.data))

    def test_get_all_bucketlists(self):
        '''Tests it can get all bucketlist'''
        self.user_registration('dan@example.org', 'StrongPwd76', 'StrongPwd76')

        response, status_code = self.user_login('dan@example.org', 'StrongPwd76')
        token = response['access_token']

        response2 = self.client().post('/api/v1/bucketlists/', headers=dict(Authorization="Bearer " + token), data=dict(name='Learn Programming'))
        self.assertEqual(response2.status_code, 201)


        response4 = self.client().post('/api/v1/bucketlists/', headers=dict(Authorization="Bearer " + token), data=dict(name='Travel the world'))
        self.assertEqual(response4.status_code, 201)

        response3 = self.client().get('/api/v1/bucketlists/', headers=dict(Authorization="Bearer " + token))

        self.assertTrue(response3.status_code == 200)
        self.assertIn('Learn Programming', str(response3.data))
        self.assertIn('Travel the world', str(response3.data))

    def test_add_new_buckelist_items(self):
        '''Test add items to bucketlist'''
        self.user_registration('dan@example.org', 'StrongPwd76', 'StrongPwd76')

        response, status_code = self.user_login('dan@example.org', 'StrongPwd76')
        token = response['access_token']

        self.client().post('/api/v1/bucketlists/', headers=dict(Authorization="Bearer " + token), data=dict(name='Learn Programming'))

        response2 = self.client().put('/api/v1/bucketlists/1', headers=dict(Authorization="Bearer " + token), data=dict(list_item_name='Python django'))

        self.assertTrue(response2.status_code == 201)
        self.assertIn('Python django', str(response2.data))


    def test_add_already_existing_buckelist_items(self):
        '''Test add items to bucketlist'''
        self.user_registration('dan@example.org', 'StrongPwd76', 'StrongPwd76')

        response, status_code = self.user_login('dan@example.org', 'StrongPwd76')
        token = response['access_token']

        self.client().post('/api/v1/bucketlists/', headers=dict(Authorization="Bearer " + token), data=dict(name='Learn Programming'))
        self.client().put('/api/v1/bucketlists/1', headers=dict(Authorization="Bearer " + token), data=dict(list_item_name='Python django'))

        response2 = self.client().put('/api/v1/bucketlists/1', headers=dict(Authorization="Bearer " + token), data=dict(list_item_name='Python django'))

        self.assertEqual(response2.status_code, 409)
        self.assertIn('Item already in bucketlist.', str(response2.data))




    def test_bucketlist_delete_list_item(self):
        '''Test it can delete an existing bucketlist item'''

        self.user_registration('dan@example.org', 'StrongPwd76', 'StrongPwd76')

        response, status_code = self.user_login('dan@example.org', 'StrongPwd76')
        token = response['access_token']

        response2 = self.client().post('/api/v1/bucketlists/', headers=dict(Authorization="Bearer " + token), data=dict(name='Learn Programming'))
        self.assertEqual(response2.status_code, 201)

        data = json.loads(response2.data.decode())

        response3 = self.client().delete('/api/v1/bucketlists/{}'.format(data['id']), headers=dict(Authorization="Bearer " + token))
        data2 = json.loads(response3.data.decode())

        self.assertEqual('Bucketlist item No {} deleted successfully'.format(data['id']), data2['message'])

    def test_bucketlist_get_list_item_by_id(self):
        '''Test it can return a list item by id'''
        pass

    def test_bucketlist_search_by_name(self):
        '''Test bucketlist items can be searched by name'''
        pass

    def test_bucketlist_pagination(self):
        '''Test the response is formatted by the requested page size'''
        pass


if __name__ == '__main__':
    unittest.main()