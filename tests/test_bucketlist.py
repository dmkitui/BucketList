import unittest
import json
from . import base_test


class BucketListEndpoints(base_test.BaseBucketListCase):
    """The bucketlist manipulation tests"""

    def test_access_not_allowed(self):
        """Tests access to bucketlist not allowed to users not logged in"""
        response = self.client().get('/api/v1/bucketlists/')
        self.assertEqual(response.status_code, 401)

        response2 = self.client().post('/api/v1/bucketlists/')
        self.assertEqual(response2.status_code, 401)

    def test_create_bucketlist(self):
        """Test it can create a bucketlist post request"""

        response = self.client().post('/api/v1/bucketlists/',
                                      headers=dict(Authorization="Bearer " + self.token),
                                      data=dict(name='Learn Programming'))

        data = json.loads(response.data.decode())

        self.assertTrue(data['name'] == 'Learn Programming')
        self.assertEqual(response.status_code, 201)

    def test_create_duplicate_bucketlist(self):
        """Test it can create a bucketlist post request"""

        self.client().post('/api/v1/bucketlists/',
                           headers=dict(Authorization="Bearer " + self.token),
                           data=dict(name='Learn Programming'))
        # Post the bucketlist again
        response = self.client().post('/api/v1/bucketlists/',
                                      headers=dict(Authorization="Bearer " + self.token),
                                      data=dict(name='Learn Programming'))

        self.assertEqual(response.status_code, 409)
        self.assertIn('Bucketlist already exists', str(response.data))

    def test_create_bucketlist_name_not_incorrect(self):
        """Test it can create a bucketlist post request"""


        response = self.client().post('/api/v1/bucketlists/',
                                      headers=dict(Authorization="Bearer " + self.token),
                                      data=dict(name=''))

        self.assertIn('Error. No bucketlist name specified', str(response.data))
        self.assertEqual(response.status_code, 400)

        response2 = self.client().post('/api/v1/bucketlists/',
                                      headers=dict(Authorization="Bearer " + self.token),
                                      data=dict(name='2017'))

        self.assertIn('Integers only not allowed for the names field', str(response2.data))
        self.assertEqual(response2.status_code, 400)


    def test_get_non_existent_bucketlist(self):
        """test get for a non-existent-bucketlist"""

        response2 = self.client().get('/api/v1/bucketlists/101',
                                      headers=dict(Authorization="Bearer " + self.token))

        self.assertTrue(response2.status_code == 404)
        self.assertIn('That bucketlist item does not exist', str(response2.data))

    def test_get_all_bucketlists(self):
        """Tests it can get all bucketlist"""

        response2 = self.client().post('/api/v1/bucketlists/',
                                       headers=dict(Authorization="Bearer " + self.token),
                                       data=dict(name='Learn Programming'))
        self.assertEqual(response2.status_code, 201)

        response3 = self.client().post('/api/v1/bucketlists/',
                                       headers=dict(Authorization="Bearer " + self.token),
                                       data=dict(name='Travel the world'))
        self.assertEqual(response3.status_code, 201)

        response4 = self.client().get('/api/v1/bucketlists/',
                                      headers=dict(Authorization="Bearer " + self.token))

        self.assertEqual(response4.status_code, 200)
        self.assertIn('Learn Programming', str(response4.data))
        self.assertIn('Travel the world', str(response4.data))

    def test_get_all_bucketlists_none_available(self):
        """test get when no buckelist exists"""

        response2 = self.client().get('/api/v1/bucketlists/',
                                      headers=dict(Authorization="Bearer " + self.token))

        self.assertEqual(response2.status_code, 200)
        self.assertIn('No bucketlists available', str(response2.data))

    def test_edit_existing_bucketlist(self):
        """Test edit an existing bucketlist"""

        self.client().post('/api/v1/bucketlists/',
                           headers=dict(Authorization="Bearer " + self.token),
                           data=dict(name='Learn Programming'))

        response2 = self.client().put('/api/v1/bucketlists/1',
                                      headers=dict(Authorization="Bearer " + self.token),
                                      data=dict(name='Learn Good Programming Skills'))

        self.assertTrue(response2.status_code == 200)
        self.assertIn('Bucketlist updated', str(response2.data))


    def test_edit_nonexistent_bucketlist(self):
        """Test edit a bucketlist that does not exist"""

        #PUT on a non-existent bucketlist
        response2 = self.client().put('/api/v1/bucketlists/105',
                                      headers=dict(Authorization="Bearer " + self.token),
                                      data=dict(name='Learn Good Programming Skills'))

        self.assertTrue(response2.status_code == 404)
        self.assertIn('That bucketlist item does not exist', str(response2.data))

    def test_edit_bucketlist_name_not_given(self):
        """Test edit a bucketlist when update name is not given"""

        self.client().post('/api/v1/bucketlists/',
                           headers=dict(Authorization="Bearer " + self.token),
                           data=dict(name='Learn Programming'))

        #PUT on a non-existent bucketlist
        response2 = self.client().put('/api/v1/bucketlists/1',
                                      headers=dict(Authorization="Bearer " + self.token),
                                      data=dict(name=''))

        self.assertTrue(response2.status_code == 400)
        self.assertIn('Error. No bucketlist name specified', str(response2.data))

    def test_edit_bucketlist_name_to_already_existing_name(self):
        """Test edit a bucketlist when update name simialr to an already existing bucketlist's 
        name"""
        self.client().post('/api/v1/bucketlists/',
                           headers=dict(Authorization="Bearer " + self.token),
                           data=dict(name='Learn Object Oriented Programming'))

        self.client().post('/api/v1/bucketlists/',
                           headers=dict(Authorization="Bearer " + self.token),
                           data=dict(name='Learn Programming'))

        #PUT with a name that is already used for another bucketlist
        response2 = self.client().put('/api/v1/bucketlists/2',
                                      headers=dict(Authorization="Bearer " + self.token),
                                      data=dict(name='Learn Object Oriented Programming'))

        self.assertTrue(response2.status_code == 409)
        self.assertIn('Bucketlist name with specified name already exists', str(response2.data))


    def test_get_bucketlist_items(self):
        """Tests it can get all bucketlist items"""
        
        response2 = self.client().post('/api/v1/bucketlists/',
                                       headers=dict(Authorization="Bearer " + self.token),
                                       data=dict(name='Learn Programming'))
        self.assertEqual(response2.status_code, 201)
        data = json.loads(response2.data.decode())
        buckelist_id = data['id']

        response4 = self.client().post('/api/v1/bucketlists/{}/items/'.format(buckelist_id),
                                      headers=dict(Authorization="Bearer " + self.token),
                                      data=dict(item_name='Intro to Java'))
        self.assertEqual(response4.status_code, 201)

        response5 = self.client().post('/api/v1/bucketlists/{}/items/'.format(buckelist_id),
                                      headers=dict(Authorization="Bearer " + self.token),
                                      data=dict(item_name='Intro to Python'))
        self.assertEqual(response5.status_code, 201)

        response6 = self.client().get('/api/v1/bucketlists/{}'.format(buckelist_id),
                                      headers=dict(Authorization="Bearer " + self.token))
        self.assertEqual(response6.status_code, 200)
        self.assertIn('Intro to Java', str(response6.data))
        self.assertIn('Intro to Python', str(response6.data))

    def test_delete_bucketlists(self):
        """Test it can delete an existing bucketlist item"""

        response2 = self.client().post('/api/v1/bucketlists/', headers=dict(Authorization="Bearer " + self.token),
                                       data=dict(name='Learn Programming'))
        self.assertEqual(response2.status_code, 201)

        data = json.loads(response2.data.decode())

        response3 = self.client().delete('/api/v1/bucketlists/{}'.format(data['id']),
                                         headers=dict(Authorization="Bearer " + self.token))
        data2 = json.loads(response3.data.decode())

        self.assertEqual(response3.status_code, 200)
        self.assertEqual('Bucketlist No {} deleted successfully'.format(data['id']), data2['message'])

    def test_edit_existing_bucketlist_items(self):
        """Test add items to bucketlist"""

        self.client().post('/api/v1/bucketlists/', headers=dict(Authorization="Bearer " + self.token),
                           data=dict(name='Learn Programming'))

        response2 = self.client().put('/api/v1/bucketlists/1', headers=dict(Authorization="Bearer " + self.token),
                                      data=dict(name='Learn Good Programming Practises'))

        self.assertEqual(response2.status_code, 200)
        self.assertIn('Bucketlist updated', str(response2.data))

        #  make same edits
        response2 = self.client().put('/api/v1/bucketlists/1',
                                      headers=dict(Authorization="Bearer " + self.token),
                                      data=dict(name='Learn Good Programming Practises'))

        self.assertEqual(response2.status_code, 409)
        self.assertIn('No changes made.', str(response2.data))

    def test_edit_bucketlist_items_name(self):
        """Test it can edit a bucketlist item's name"""

        response2 = self.client().post('/api/v1/bucketlists/', headers=dict(Authorization="Bearer " + self.token),
                                       data=dict(name='Learn Programming'))
        self.assertEqual(response2.status_code, 201)

        data = json.loads(response2.data.decode())
        buckelist_id = data['id']

        response3 = self.client().post('/api/v1/bucketlists/{}/items/'.format(buckelist_id),
                                      headers=dict(Authorization="Bearer " + self.token),
                                      data=dict(item_name='Intro to Python'))

        data = json.loads(response3.data.decode())
        item_id = data['id']

        response4 = self.client().put('/api/v1/bucketlists/{}/items/{}'.format(buckelist_id, item_id),
                                      headers=dict(Authorization="Bearer " + self.token),
                                      data=dict(item_name='Python fundamentals and syntax'))
        data = json.loads(response4.data.decode())

        self.assertEqual(response4.status_code, 201)
        self.assertIn('Item {} successfully updated'.format(item_id), data['message'])

    def test_edit_bucketlist_items_status(self):
        """Test it can edit a bucketlist item's done status"""

        response2 = self.client().post('/api/v1/bucketlists/', headers=dict(Authorization="Bearer " + self.token),
                                       data=dict(name='Learn Programming'))
        self.assertEqual(response2.status_code, 201)

        data = json.loads(response2.data.decode())
        buckelist_id = data['id']

        response3 = self.client().post('/api/v1/bucketlists/{}/items/'.format(buckelist_id),
                                      headers=dict(Authorization="Bearer " + self.token),
                                      data=dict(item_name='Intro to Python'))

        data = json.loads(response3.data.decode())
        item_id = data['id']

        response4 = self.client().put('/api/v1/bucketlists/{}/items/{}'.format(buckelist_id, item_id),
                                      headers=dict(Authorization="Bearer " + self.token),
                                      data=dict(done=True))
        data = json.loads(response4.data.decode())
        print(data)

        self.assertEqual(response4.status_code, 201)
        self.assertEqual(data['done'], True)
        self.assertIn('Item {} successfully updated'.format(item_id), data['message'])


    def test_edit_none_existent_bucketlist_item(self):
        """Test it can edit a bucketlist item that does not exist"""

        response2 = self.client().post('/api/v1/bucketlists/', headers=dict(Authorization="Bearer " + self.token),
                                       data=dict(name='Learn Programming'))
        self.assertEqual(response2.status_code, 201)

        data = json.loads(response2.data.decode())
        buckelist_id = data['id']

        response3 = self.client().delete('/api/v1/bucketlists/{}/items/108'.format(buckelist_id),
                                      headers=dict(Authorization="Bearer " + self.token),
                                      data=dict(item_name='Intro to Python'))

        data = json.loads(response3.data.decode())
        self.assertEqual(response3.status_code, 404)
        self.assertIn('That bucketlist item does not exist', data['message'])

    def test_add_item_to_non_existent_bucketlist(self):
        """Test it cannot add item to a non existent bucketlist item"""

        response3 = self.client().post('/api/v1/bucketlists/345/items/',
                                      headers=dict(Authorization="Bearer " + self.token),
                                      data=dict(item_name='Visit Japan'))

        data = json.loads(response3.data.decode())
        self.assertEqual(response3.status_code, 404)
        self.assertEqual('That bucketlist does not exist', data['message'])

    def test_add_item_that_already_exists(self):
        """Test it cannot add item to when it already exists"""

        response2 = self.client().post('/api/v1/bucketlists/', headers=dict(Authorization="Bearer " + self.token),
                                       data=dict(name='Travel the world'))
        self.assertEqual(response2.status_code, 201)

        data = json.loads(response2.data.decode())
        buckelist_id = data['id']

        response3 = self.client().post('/api/v1/bucketlists/{}/items/'.format(buckelist_id),
                                      headers=dict(Authorization="Bearer " + self.token),
                                      data=dict(item_name='Visit Japan'))

        self.assertEqual(response3.status_code, 201)
        # Add the same bcketlist item again
        response4 = self.client().post('/api/v1/bucketlists/{}/items/'.format(buckelist_id),
                                      headers=dict(Authorization="Bearer " + self.token),
                                      data=dict(item_name='Visit Japan'))

        data = json.loads(response4.data.decode())
        self.assertEqual(response4.status_code, 409)
        self.assertEqual('The item already in list', data['message'])


    def test_edit_bucketlist_items_no_parameters(self):
        """Test it cannot edit a bucketlist item when no update parameters are given"""

        response2 = self.client().post('/api/v1/bucketlists/', headers=dict(Authorization="Bearer " + self.token),
                                       data=dict(name='Learn Programming'))
        self.assertEqual(response2.status_code, 201)

        data = json.loads(response2.data.decode())
        buckelist_id = data['id']

        response3 = self.client().post('/api/v1/bucketlists/{}/items/'.format(buckelist_id),
                                      headers=dict(Authorization="Bearer " + self.token),
                                      data=dict(item_name='Intro to Python'))

        data = json.loads(response3.data.decode())
        item_id = data['id']

        response4 = self.client().put('/api/v1/bucketlists/{}/items/{}'.format(buckelist_id, item_id),
                                      headers=dict(Authorization="Bearer " + self.token))
        data = json.loads(response4.data.decode())

        self.assertEqual(response4.status_code, 409)
        self.assertIn('No update made', data['message'])


    def test_delete_bucketlist_item(self):
        """Test it can delete a bucketlist item"""

        response2 = self.client().post('/api/v1/bucketlists/', headers=dict(Authorization="Bearer " + self.token),
                                       data=dict(name='Learn Programming'))
        self.assertEqual(response2.status_code, 201)

        data = json.loads(response2.data.decode())
        bucketlist_id = data['id']

        response3 = self.client().post('/api/v1/bucketlists/{}/items/'.format(bucketlist_id),
                                      headers=dict(Authorization="Bearer " + self.token),
                                      data=dict(item_name='Intro to Python'))

        data2 = json.loads(response3.data.decode())
        item_id = data2['id']

        response4 = self.client().delete(
            '/api/v1/bucketlists/{}/items/{}'.format(bucketlist_id,item_id),
            headers=dict(Authorization="Bearer " + self.token))
        data = json.loads(response4.data.decode())

        self.assertEqual(response4.status_code, 200)

        self.assertEqual('Bucketlist item No {} deleted successfully'.format(item_id), data['message'])

    def test_delete_bucketlist_item_in_bucketlist_that_does_exist(self):
        """Test delete item for a bucketlist that does not exist"""

        response = self.client().delete('/api/v1/bucketlists/12020/items/129',
            headers=dict(Authorization="Bearer " + self.token))
        data = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 404)

        self.assertEqual('That bucketlist does not exist', data['message'])


    def test_bucketlist_search_not_found(self):
        """Test bucketlist search by name no results"""
        response1 = self.client().post('/api/v1/bucketlists/', headers=dict(Authorization="Bearer " + self.token),
                                       data=dict(name='Learn Programming'))

        self.assertEqual(response1.status_code, 201)

        response2 = self.client().get('/api/v1/bucketlists/?q=travel',
                                      headers=dict(Authorization="Bearer " + self.token))

        self.assertEqual(response2.status_code, 404)
        self.assertIn('No bucketlists with provided search parameter', str(response2.data))


    def test_bucketlist_search_no_search_parameter(self):
        """Test bucketlist search when no parameter given"""

        response2 = self.client().get('/api/v1/bucketlists/?q=',
                                      headers=dict(Authorization="Bearer " + self.token))

        self.assertEqual(response2.status_code, 400)
        self.assertIn('Query parameter cannot be empty', str(response2.data))


    def test_search_success(self):
        """test search functionality, success"""
        response1 = self.client().post('/api/v1/bucketlists/', headers=dict(Authorization="Bearer " + self.token),
                                       data=dict(name='Learn Programming'))

        self.assertEqual(response1.status_code, 201)

        response2 = self.client().get('/api/v1/bucketlists/?q=program',
                                      headers=dict(Authorization="Bearer " + self.token))

        self.assertEqual(response2.status_code, 200)
        self.assertIn('Learn Programming', str(response2.data))


    def test_bucketlist_pagination(self):
        """Test the page limit restrictions"""
        response = self.client().get('/api/v1/bucketlists/?limit=101',
                                      headers=dict(Authorization="Bearer " + self.token))

        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid limit value. Valid values are 1-100', str(response.data))

        response2 = self.client().get('/api/v1/bucketlists/?limit=no',
                                      headers=dict(Authorization="Bearer " + self.token))

        self.assertEqual(response2.status_code, 400)
        self.assertIn('Limit parameter can only be a positive integer', str(response2.data))

if __name__ == '__main__':
    unittest.main()
