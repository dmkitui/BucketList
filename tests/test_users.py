import unittest

# from app import create_app, db
from app.main_app import create_app, db
from base import BaseTestCase



class UsersModelTestCase(BaseTestCase):
    '''Testcase for the users model'''

    def test_valid_user_registration(self):
        '''Test for a user registration'''
        response = self.user_registration('user@gmail.com', 'Password01', 'Password01')
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'Registration successful, welcome to Bucketlist', response.data)

    def test_invalid_registration_wrong_passwords_match(self):
        '''Tests a wrong password match'''
        response = self.user_registration('user2@gmail.com', 'Password01', 'PASSWORD01')
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Password fields do not match', response.data)

    def test_user_registration_weak_password(self):
        '''Test for registartion using weak password'''
        response = self.user_registration('user010@example.com', 'password', 'password')
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Weak password. Make sure password contains at least 8 characters, an uppercase letter, and a digit', response.data)

    def test_duplicate_user_registration(self):
        '''Tests to prevent an already registred email being used again'''
        response = self.user_registration('dan@gmail.com', 'Password01', 'Password01')
        self.assertEqual(response.status_code, 201)

        #Register using same email address again
        response = self.user_registration('dan@gmail.com', 'passworD02', 'passworD02')
        self.assertEqual(response.status_code, 202)     # The request was received, but wont be acted uopn
        self.assertIn(b'Registration Failure. User dan@gmail.com already registered', response.data)

    def test_user_login_not_registered(self):
        '''Test for login by unregistered user'''
        response = self.user_login('notregistered@example.com', 'qwerty')  # Create new user
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'User notregistered@example.com does not exist. Register to access the service', response.data)

    def test_user_login_valid_credentials(self):
        '''test for a successful user login'''

        response = self.user_registration('newuser@gmail.com', 'Qwerty03', 'Qwerty03')  # Create new user
        self.assertEqual(response.status_code, 201)

        # Login
        response = self.user_login('newuser@gmail.com', 'Qwerty03')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login successful', response.data)

    def test_user_login_invalid_password(self):
        '''Test for login with invalid password'''
        response = self.user_registration('newuser1@gmail.com', 'Qwerty04', 'Qwerty04')  # Create new user
        self.assertEqual(response.status_code, 201)

        # Login with invalid credentials
        response = self.user_login('newuser1@gmail.com', 'wrong_password')
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Invalid email or password', response.data)

    def tearDown(self):
        '''Clean up the test environment'''
        with self.app.app_context():
            db.session.remove()
            db.drop_all()