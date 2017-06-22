from . import base

class UsersModelTestCase(base.BaseTestCase):
    '''Testcase for the users model'''

    def test_valid_user_registration(self):
        '''Test for a user registration'''
        response, status_code = self.user_registration('user@gmail.com', 'Password01', 'Password01')

        self.assertEqual(status_code, 201)
        self.assertEqual(response['message'], 'Registration successful, welcome to Bucketlist')

    def test_invalid_registration_wrong_passwords_match(self):
        '''Tests a wrong password match'''
        response, status_code = self.user_registration('user2@gmail.com', 'Password01', 'PASSWORD01')

        self.assertEqual(status_code, 401)
        self.assertEqual(response['message'], 'Password fields do not match')

    def test_invalid_registration_no_email_provided(self):
        '''Tests a wrong password match'''
        response, status_code = self.user_registration('', 'Password01', 'PASSWORD01')

        self.assertEqual(status_code, 401)
        self.assertEqual(response['message'], 'Email or password cannot be blank')

    def test_user_registration_weak_password(self):
        '''Test for registartion using weak password'''
        response, status_code = self.user_registration('user010@example.com', 'password', 'password')

        self.assertEqual(status_code, 401)
        self.assertEqual(response['message'], 'Weak password. Make sure password contains at least 8 characters, an uppercase letter, and a digit')

    def test_duplicate_user_registration(self):
        '''Tests to prevent an already registred email being used again'''
        response, status_code = self.user_registration('dan@gmail.com', 'Password01', 'Password01')

        self.assertEqual(status_code, 201)
        self.assertTrue(response['message'] == 'Registration successful, welcome to Bucketlist')

        #Register using same email address again
        response, status_code2 = self.user_registration('dan@gmail.com', 'passworD02', 'passworD02')
        self.assertEqual(status_code2, 202)     # The request was received, but wont be acted uopn
        self.assertEqual(response['message'], 'Registration Failure. User dan@gmail.com already registered')

    def test_user_login_not_registered(self):
        '''Test for login by unregistered user'''
        response, status_code = self.user_login('notregistered@example.com', 'qwerty')  # Create new user

        self.assertEqual(status_code, 401)
        self.assertEqual(response['message'], 'User notregistered@example.com does not exist. Register to access the service')

    def test_user_login_valid_credentials(self):
        '''test for a successful user login'''

        response, status_code = self.user_registration('newuser@gmail.com', 'Qwerty03', 'Qwerty03')  # Create new user
        self.assertEqual(status_code, 201)

        # Login
        response, status_code2 = self.user_login('newuser@gmail.com', 'Qwerty03')
        self.assertEqual(status_code2, 200)
        self.assertTrue(response['access_token'])
        self.assertTrue(response['message'] == 'Login successful')

    def test_user_login_invalid_password(self):
        '''Test for login with invalid password'''
        response, status_code = self.user_registration('newuser1@gmail.com', 'Qwerty04', 'Qwerty04')  # Create new user

        self.assertEqual(status_code, 201)

        # Login with invalid credentials
        response, status_code = self.user_login('newuser1@gmail.com', 'wrong_password')
        self.assertEqual(status_code, 401)
        self.assertTrue(response['message'] == 'Invalid email or password')

    def test_user_login_blank_details(self):
        '''Test for login with invalid password'''
        response, status_code = self.user_registration('newuser1@gmail.com', 'Qwerty04', 'Qwerty04')  # Create new user

        self.assertEqual(status_code, 201)

        # Login with invalid credentials: blank user_email
        response, status_code = self.user_login('', 'wrong_password')
        self.assertEqual(status_code, 401)
        self.assertTrue(response['message'] == 'Email or password cannot be blank')

        # Login with invalid credentials: blank password
        response, status_code = self.user_login('newuser1@gmail.com', '')
        self.assertEqual(status_code, 401)
        self.assertTrue(response['message'] == 'Email or password cannot be blank')

    def test_post__invalid_token(self):
        '''test for when a user logins invalid token'''

        self.user_registration('dan@example.org', 'StrongPwd76', 'StrongPwd76')

        self.user_login('dan@example.org', 'StrongPwd76')
        # Invalid token
        token = 'no2344324ewefsdfdf8sdf0sdf0sdfsdf77fwrwewerew'

        response2 = self.client().post('/api/v1/bucketlists/', headers=dict(Authorization="Bearer " + token), data=dict(name='Learn Programming'))

        self.assertEqual(response2.status_code, 401)
