from copy import copy, deepcopy
from unittest import skip
from poim_api.utils.tests import TestCase, MultipleUsersTestMixin


class RegistrationMixin:
    registration_path = '/register'
    register_data = {
        'username': 'user',
        'email': 'user@example.com',
        'password': 'password user',
        'first_name': 'John',
        'last_name': 'Smith',
    }


class RegistrationTestCase(RegistrationMixin, TestCase):
    def test_registration(self):
        response = self.client.post(self.registration_path, data=self.register_data)
        self.assertEqual(response.status_code, 201)

        profile = response.json()['profile']

        for field in ['username', 'email', 'first_name']:
            self.assertEqual(profile.get(field), self.register_data[field],
                msg='"{}" field in profile data mismatched.'.format(field))

        self.assertIn('has_usable_password', profile)
        self.assertTrue(profile['has_usable_password'])

    def test_unique_check(self):
        response = self.client.post(self.registration_path, data=self.register_data)
        self.assertEqual(response.status_code, 201)

        response = self.client.post(self.registration_path, data=self.register_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json().keys()), set(['email', 'username']))

    def test_username_case_sensetive(self):
        register_data = copy(self.register_data)

        response = self.client.post(self.registration_path, data=register_data)
        self.assertEqual(response.status_code, 201)

        register_data['username'] = 'User'
        register_data['email'] = 'user+1@example.com'

        response = self.client.post(self.registration_path, data=register_data)
        self.assertEqual(response.status_code, 201)

    def test_email_case_insensetive(self):
        register_data = copy(self.register_data)

        response = self.client.post(self.registration_path, data=register_data)
        self.assertEqual(response.status_code, 201)

        register_data['username'] = 'user2'
        for email in ['User@example.com', 'user@Example.com']:
            register_data['email'] = email
            response = self.client.post(self.registration_path, data=register_data)
            self.assertEqual(response.status_code, 400, msg='for email {}'.format(email))
            self.assertEqual(set(response.json().keys()), set(['email']), msg='for email {}'.format(email))

    def test_required_fields(self):
        response = self.client.post(self.registration_path, data={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json().keys()), set(self.register_data.keys()))

    def test_empty_fields(self):
        response = self.client.post(self.registration_path, data={
            'username': '',
            'email': '',
            'password': '',
            'first_name': '',
            'last_name': '',
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json().keys()), set(self.register_data.keys()))

    def test_invalid_email(self):
        request_data = copy(self.register_data)
        request_data['email'] = 'abc'
        response = self.client.post(self.registration_path, data=request_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json().keys()), set(['email']))

    def test_short_password(self):
        request_data = copy(self.register_data)
        request_data['password'] = 'acd$'
        response = self.client.post(self.registration_path, data=request_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json().keys()), set(['password']))

    def test_options(self):
        response = self.client.options(self.registration_path, HTTP_ACCESS_CONTROL_REQUEST_METHOD='POST')
        self.assertEqual(response.status_code, 200)


class MultiUserRegistrationTestCase(RegistrationMixin, MultipleUsersTestMixin, TestCase):
    def test_registration_while_authenticated(self):
        response = self.alice_client.post(self.registration_path, data=self.register_data)
        self.assertEqual(response.status_code, 201)
        auth_token = response.json()['auth_token']
        self.assertNotEqual(auth_token, self.auth_tokens['alice'])

    def test_registration_with_invalid_token(self):
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Token non_existent5580c82836cfd9b51bc96e4ae193b9968'
        response = self.client.post(self.registration_path, data=self.register_data)
        self.assertEqual(response.status_code, 401)


class AuthenticationTestCase(MultipleUsersTestMixin, TestCase):
    login_path = '/login'
    logout_path = '/logout'
    auth_data = {
        'username': 'alice',
        'password': 'password alice',
    }

    def test_login(self):
        response = self.client.post(self.login_path, data=self.auth_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['profile'], self.profiles['alice'])

    def test_login_while_authenticated(self):
        response = self.alice_client.post(self.login_path, data=self.auth_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['profile'], self.profiles['alice'])
        self.assertEqual(response.json()['auth_token'], self.auth_tokens['alice'])

    def test_other_user_login_while_authenticated(self):
        response = self.bob_client.post(self.login_path, data=self.auth_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['profile'], self.profiles['alice'])
        auth_token = response.json()['auth_token']
        self.assertEqual(auth_token, self.auth_tokens['alice'])

    def test_login_with_invalid_token(self):
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Token non_existent5580c82836cfd9b51bc96e4ae193b9968'

        response = self.client.post(self.login_path, data=self.auth_data)
        self.assertEqual(response.status_code, 401)

    def test_value_strip(self):
        response = self.client.post(self.login_path, data={
            'username': ' alice ',
            'password': 'password alice',
        })
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.login_path, data={
            'username': 'alice',
            'password': ' password alice ',
        })
        self.assertEqual(response.status_code, 200)

    def test_username_case_sensetive(self):
        response = self.client.post(self.login_path, data={
            'username': 'Alice',
            'password': 'password alice',
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json().keys()), set(['non_field_errors']))

    def test_login_password_validation(self):
        response = self.client.post(self.login_path, data={
            'username': 'alice',
            'password': 'password bob',
        })
        self.assertEqual(response.status_code, 400)

        response = self.client.post(self.login_path, data={
            'username': 'alice',
            'password': '',
        })
        self.assertEqual(response.status_code, 400)

    def test_required_fields(self):
        response = self.client.post(self.login_path, data={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json().keys()), set(['username', 'password']))

    def test_empty_fields(self):
        response = self.client.post(self.login_path, data={
            'username': '',
            'password': '',
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json().keys()), set(['username', 'password']))

    def test_logout(self):
        response = self.client.post(self.login_path, data=self.auth_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['profile'], self.profiles['alice'])
        auth_token = response.json()['auth_token']

        self.client.defaults['HTTP_AUTHORIZATION'] = 'Token '+auth_token

        response = self.client.post(self.logout_path)
        self.assertEqual(response.status_code, 204)

        response = self.client.post(self.logout_path)
        self.assertEqual(response.status_code, 401)

        response = self.alice_client.post(self.logout_path)
        self.assertEqual(response.status_code, 401)

        response = self.bob_client.post(self.logout_path)
        self.assertEqual(response.status_code, 204)

    def test_options(self):
        response = self.client.options(self.login_path, HTTP_ACCESS_CONTROL_REQUEST_METHOD='POST')
        self.assertEqual(response.status_code, 200)

        response = self.client.options(self.logout_path, HTTP_ACCESS_CONTROL_REQUEST_METHOD='POST')
        self.assertEqual(response.status_code, 200)
