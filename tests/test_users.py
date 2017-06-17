import unittest

# from app import create_app, db
from app.main_app import create_app, db
from base import BaseTestCase



class UsersModelTestCase(BaseTestCase):
    '''Testcase for the users model'''

    def test_valid_user_registration(self):
        '''Test for a user registration'''
        response = self.user_registration('user@gmail.com', 'password', 'password')
        self.assertEqual(response.status_code, 201)
        self.assertIn('Registration successful, welcome to Bucketlist', response.data)

    def test_invalid_registration_wrong_passwords_match(self):
        '''Tests a wrong password match'''
        response = self.user_registration('user@gmail.com', 'password', 'PASSWORD')
        self.assertEqual(response.status_code, 401)
        self.assertIn('Passwords do not match', response.data)

    def test_duplicate_user_registration(self):
        '''Tests to prevent an already registred email being used again'''
        response = self.user_registration('dan@gmail.com', 'password', 'password')
        self.assertEqual(response.status_code, 201)

        #Register using same email address again
        response = self.user_registration('dan@gmail.com', 'password', 'password')
        self.assertEqual(response.status_code, 202)     # The request was received, but wont be acted uopn
        self.assertIn('Registration Failure. User dan@gmail.com already registered', response.data)

    def tearDown(self):
        '''Clean up the test environment'''
        with self.app.app_context():
            db.session.remove()
            db.drop_all()