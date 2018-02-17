from . import base_test
import time

class UsersModelTestCase(base_test.BaseTestCase):
    '''Testcase for the users model'''

    def test_valid_user_registration(self):
        '''Test for a user registration'''
        response, status_code = self.user_registration('user@gmail.com', 'Password01', 'Password01', 'alphadog')

        self.assertEqual(status_code, 201)
        self.assertEqual(response['message'], 'Registration successful, welcome to Bucketlist')

    def test_invalid_registration_wrong_passwords_match(self):
        '''Tests a wrong password match'''
        response, status_code = self.user_registration('user2@gmail.com', 'Password01', 'PASSWORD01', 'alphadog')

        self.assertEqual(status_code, 400)
        self.assertIn('Password fields do not match', response.values())

    def test_invalid_registration_no_email_provided(self):
        '''Tests a wrong password match'''
        response, status_code = self.user_registration('', 'Password01', 'PASSWORD01', 'alphadog')

        self.assertEqual(status_code, 400)
        self.assertIn('Not a valid email address.', response['user_email'])

    def test_user_registration_weak_password(self):
        '''Test for registartion using weak password'''
        response, status_code = self.user_registration('user010@example.com', 'password', 'password', 'alphadog')

        self.assertEqual(status_code, 400)
        self.assertEqual(response['message'],
                         'Weak password. Make sure password contains at least 8 characters, an uppercase letter, and a digit')

    def test_duplicate_user_registration(self):
        '''Tests to prevent an already registred email being used again'''
        response, status_code = self.user_registration('dan@gmail.com', 'Password01', 'Password01', 'alphadog')

        self.assertEqual(status_code, 201)
        self.assertTrue(response['message'] == 'Registration successful, welcome to Bucketlist')

        #Register using same email address again
        response, status_code2 = self.user_registration('dan@gmail.com', 'passworD02', 'passworD02', 'alphadog')
        self.assertEqual(status_code2, 409)     # The request was received, but wont be acted uopn
        self.assertEqual(
            'Registration Failure. User dan@gmail.com already registered', response['message'])

    def test_user_login_not_registered(self):
        '''Test for login by unregistered user'''
        response, status_code = self.user_login('notregistered@example.com', 'qwerty', 'username')  # Create new user

        self.assertEqual(status_code, 401)
        self.assertEqual('User notregistered@example.com does not exist. Register to access the '
                      'service', response['message'])

    def test_user_login_valid_credentials(self):
        '''test for a successful user login'''

        response, status_code = self.user_registration('newuser@gmail.com', 'Qwerty03', 'Qwerty03', 'alphadog')  # Create new user
        self.assertEqual(status_code, 201)

        # Login
        response, status_code2 = self.user_login('newuser@gmail.com', 'Qwerty03', 'username')
        self.assertEqual(status_code2, 200)
        self.assertTrue(response['access_token'])
        self.assertTrue(response['message'] == 'Login successful')

    def test_user_login_invalid_password(self):
        '''Test for login with invalid password'''
        response, status_code = self.user_registration('newuser1@gmail.com', 'Qwerty04', 'Qwerty04', 'alphadog')  # Create new user

        self.assertEqual(status_code, 201)

        # Login with invalid credentials
        response, status_code = self.user_login('newuser1@gmail.com', 'wrong_password', 'username')
        self.assertEqual(status_code, 401)
        self.assertTrue(response['message'] == 'Incorrect email or password')

    def test_user_login_blank_details(self):
        '''Test for login with invalid password'''
        response, status_code = self.user_registration('newuser1@gmail.com', 'Qwerty04', 'Qwerty04', 'alphadog')  # Create new user

        self.assertEqual(status_code, 201)

        # Login with invalid credentials: blank user_email
        response, status_code = self.user_login('', 'wrong_password', 'username')
        self.assertEqual(status_code, 400)
        self.assertIn('Not a valid email address.', response['user_email'])

        # Login with invalid credentials: blank password
        response, status_code = self.user_login('newuser1@gmail.com', '', 'username')
        self.assertEqual(status_code, 401)
        self.assertEqual('Incorrect email or password', response['message'])

    def test_post__invalid_token(self):
        '''test for when a user logins invalid token'''

        self.user_registration('dan@example.org', 'StrongPwd76', 'StrongPwd76', 'alphadog')

        self.user_login('dan@example.org', 'StrongPwd76', 'username')
        # Invalid token
        token = 'no2344324ewefsdfdf8sdf0sdf0sdfsdf77fwrwewerew'

        response2 = self.client().post('/api/v1/bucketlists/',
                                       headers=dict(Authorization="Bearer " + token),
                                       data=dict(name='Learn Programming'))

        self.assertEqual(response2.status_code, 401)

    def test_expired_toke(self):
        """Tests for an expired token"""
        self.user_registration('dan@example.org', 'StrongPwd76', 'StrongPwd76', 'alphadog')

        response, status_code = self.user_login('dan@example.org', 'StrongPwd76', 'username')
        # Get the token
        token = response['access_token']

        time.sleep(10)
        response2 = self.client().get('/api/v1/bucketlists/',
                                      headers=dict(Authorization="Bearer " + token))

        self.assertEqual(response2.status_code, 401)
