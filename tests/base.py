import unittest

# from app import create_app, db
from app.main_app import create_app, db

class BaseTestCase(unittest.TestCase):
    '''Base test case configuration'''

    def setUp(self):
        '''Setup method for each test case'''

        self.app = create_app(config_name='testing')
        self.client = self.app.test_client

        with self.app.app_context():  # Bind the app to current context
            db.create_all()  # create the tables


    # Helper methods
    def user_registration(self, email, password, confirm_password):
        '''
        Helper method to register a new user
        :param email: user email address
        :param password: user password
        :param confrim_password: user password entered gain to confirm
        :return: POST to the regoster endpoint
        '''
        return self.app.post('/register', data=dict(email=email, password=password, confirm_password=confirm_password, follow_redirects=True))


    def user_login(self, email, password):
        '''
        Helper method to login a user
        :param email: user email
        :param password: user password
        :return: POST to the login endpoint
        '''
        return self.app.post('/login', data=dict(email=email, password=password, follow_redirects=True))


    def user_logout(self):
        '''
        Helper method to logout a user
        :return: GET to the logout endpoint
        '''
        return self.app.get('/logout', follow_redirects=True)