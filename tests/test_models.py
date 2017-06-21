from base import BaseTestCase
from app.models import User, Bucketlists, BucketListItems
from app.main_app import create_app, db
import unittest



class ModelsTests(unittest.TestCase):
    '''Class for the model tests'''

    def setUp(self):
        self.app = create_app(config_name='testing')
        self.client = self.app.test_client
        db.create_all()  # create the tables

        self.user_email = 'dan@example.org'
        self.user_password = 'password0122'
        self.person = User(self.user_email, self.user_password)

    def tearDown(self):
        db.session.close()
        db.drop_all()


    def test_add_person(self):
        '''Test it adds a user to the database'''

        initial_users_count = len(User.query.all())
        self.person.save()
        users_count = User.query.all()

        self.assertEqual((initial_users_count + 1), len(users_count))

    def test_it_generates_a_user_token(self):
        '''Test it generates a user token'''
        pass



    def test_query_user_by_email(self):
        '''Test for the User model'''
        self.person.save()
        person_obj = User.query.filter_by(user_email='dan@example.org').first()
        self.assertTrue(person_obj.user_email == 'dan@example.org')

    def test_query_user_by_id(self):
        '''Test it ca nget a user given the user's id'''

        self.person.save()

        person_id_to_search = 1
        person_obj = User.query.filter_by(id=person_id_to_search).first()
        self.assertEqual(self.user_email, person_obj.user_email)

        ## Test it hashes a password?

    def test_bucketlists(self):
        '''test it can add bucketlists'''

        self.person.save()
        person_id = self.person.id
        initial_bucketlistcount = len(Bucketlists.query.all())

        bucketlist1 = Bucketlists('Travel the world', person_id)
        bucketlist1.save()

        current_count = len(Bucketlists.query.all())

        self.assertTrue(current_count == (initial_bucketlistcount + 1))

    def test_query_bucketlist_by_user_id(self):
        '''Test it can return a list of a users bucketlists given a user id'''

        self.person.save()

        person_id = self.person.id
        bucketlist1 = Bucketlists('Travel the world', person_id)
        bucketlist1.save()

        query = Bucketlists.query.filter_by(owner_id=person_id).first()

        self.assertEqual(query.name, 'Travel the world')


    def test_bucketlist_items(self):
        '''Test it can add bucketlist items'''

        self.person.save()
        initial_count = len(BucketListItems.query.all())

        person_id = self.person.id

        bucketlist1 = Bucketlists('Travel the world', person_id)
        bucketlist1.save()

        bucketlist_items = BucketListItems('Visit Thailand this year', bucketlist1.id)
        bucketlist_items.save()

        current_count = len(BucketListItems.query.all())

        self.assertTrue(current_count == (initial_count + 1))
















