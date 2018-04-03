import json
from django.test import Client, TestCase as DjangoTestCase
from django.test.client import JSON_CONTENT_TYPE_RE


class APIClient(Client):
    api_version = None

    def __init__(self, **defaults):
        if self.api_version:
            if isinstance(self.api_version, str):
                defaults['HTTP_X_API_VERSION'] = self.api_version
            else:
                defaults['HTTP_X_API_VERSION'] = '{}.{}'.format(self.api_version)

        defaults['HTTP_ACCEPT'] = 'application/json; charset=utf-8'
        defaults['HTTP_ACCEPT_LANGUAGE'] = 'ru'
        super().__init__(**defaults)

    def _content_type_is_json(self, content_type):
        return bool(JSON_CONTENT_TYPE_RE.match(content_type))

    def _encode_data(self, data, content_type):
        if self._content_type_is_json(content_type):
            return data
        return super()._encode_data(data, content_type)

    def generic(self, method, path, data=None, content_type='application/json', secure=False, **extra):
        if self._content_type_is_json(content_type):
            data = json.dumps(data)

        response = super().generic(method, path, data=data, content_type=content_type, secure=secure, **extra)

        # data содержит нативный объект. Сброс удобен для страховки от прямого ображения вместо json().
        response.data = None

        return response

    def post(self, path, data=None, content_type='application/json', follow=False, secure=False, **extra):
        return super().post(path, data=data, content_type=content_type, follow=follow, secure=secure, **extra)

    def options(self, path, data=None, content_type='application/json', follow=False, secure=False, **extra):
        return super().options(path, data=data, content_type=content_type, follow=follow, secure=secure, **extra)

    def put(self, path, data=None, content_type='application/json', follow=False, secure=False, **extra):
        return super().put(path, data=data, content_type=content_type, follow=follow, secure=secure, **extra)

    def patch(self, path, data=None, content_type='application/json', follow=False, secure=False, **extra):
        return super().patch(path, data=data, content_type=content_type, follow=follow, secure=secure, **extra)

    def delete(self, path, data=None, content_type='application/json', follow=False, secure=False, **extra):
        return super().delete(path, data=data, content_type=content_type, follow=follow, secure=secure, **extra)


class TestCase(DjangoTestCase):
    maxDiff = None

    def setUp(self):
        super().setUp()
        self.client = APIClient()


class MultipleUsersTestMixin:
    usernames = ['alice', 'bob', 'carol']

    def setUp(self):
        super().setUp()
        self.client = APIClient()

        self.profiles = {}
        self.auth_tokens = {}

        for i, name in enumerate(self.usernames):
            register_data = {
                'username': name,
                'email': '{}@example.com'.format(name),
                'password': 'password '+name,
                'first_name': name.capitalize(),
                'last_name': 'Smith',
            }

            response = self.client.post('/register', data=register_data)
            self.assertEqual(response.status_code, 201)

            self.profiles[name] = response.json()['profile']
            auth_token = response.json()['auth_token']
            self.auth_tokens[name] = auth_token

            client = APIClient()
            client.defaults['HTTP_AUTHORIZATION'] = 'Token '+auth_token
            setattr(self, '{}_client'.format(name), client)
