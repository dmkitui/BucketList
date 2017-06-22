import unittest
import json
# from app.models import User, BucketListItems, Bucketlists

# from app.main_app import create_app, db
from app import bucketlist_app

db = bucketlist_app.db
User = bucketlist_app.User


class BaseTestCase(unittest.TestCase):
    '''Base test case configuration'''

    def setUp(self):
        '''Setup method for each test case'''

        self.app = bucketlist_app.create_app(config_name='testing')
        self.client = self.app.test_client

        with self.app.app_context():  # Bind the app to current context
            db.create_all()  # create the tables



    # Helper methods
    def user_registration(self, email, password, confirm_password):
        '''
        Helper method to register a new user
        :param email: user email address
        :param password: user password
        :param confrim_password: user password entered again to confirm
        :return: POST response to the api/auth/register endpoint
        '''
        response = self.client().post('/api/v1/auth/register', data=dict(user_email=email,
                                                                         user_password=password,
                                                                         confirm_password=confirm_password,
                                                                         follow_redirects=True))

        return json.loads(response.data.decode()), response.status_code

    def user_login(self, email, password):
        '''
        Helper method to login a user
        :param email: user email
        :param password: user password
        :return: POST to the login endpoint
        '''

        response = self.client().post('/api/v1/auth/login', data=dict(user_email=email,
                                                                      user_password=password,
                                                                      follow_redirects=True))

        return json.loads(response.data.decode()), response.status_code


    def user_logout(self):
        '''
        Helper method to logout a user
        :return: GET to the logout endpoint
        '''
        return self.client().get('/api/v1/auth/logout', follow_redirects=True)

    def tearDown(self):
        with self.app.app_context():  # Bind the app to current context
            db.session.close()
            db.drop_all()

class BaseBucketListCase(BaseTestCase):
    '''Tests configuration for bucketlist tests'''

    def setUp(self):
        self.app = bucketlist_app.create_app(config_name='testing')
        self.client = self.app.test_client

        with self.app.app_context():  # Bind the app to current context
            db.session.close()
            db.drop_all()
            db.create_all()  # create the tables

    def logged_valid_user(self):
        '''Helper method for a logged in user'''
        pass
