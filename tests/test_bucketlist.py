import unittest
import sys
import os

# from app import create_app, db
# from app import create_app, db
# topdir = os.path.join(os.path.dirname(__file__), "..")
# sys.path.append(topdir)
from base import BaseTestCase


class BucketList_DB(BaseTestCase):
    '''The bucketlist base tests'''

    def test_bucketlist_create_list_item(self):
        '''Test it can create a bucketlist post request'''

        response = self.client.post('/bucketlists', data=self.bucketlist)
        self.assertEqual(response.status_code, 201)
        self.assertIn('Become a world a class developer', str(response.data))

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