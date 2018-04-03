from copy import copy, deepcopy
from unittest import skip
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from poim_api.utils.tests import TestCase, MultipleUsersTestMixin


User = get_user_model()


class PointGenericMixin:
    point_create_path = '/points'
    point_list_path = '/points'
    point_detail_path = '/points/{id}'
    point_undelete_path = point_detail_path + '/deleted'

    point_data = {
        'title': 'My point',
        'latitude': 59.876364,
        'longitude': 30.32522,
        'unlisted': False,
    }

    point_empty_data = {
        'title': '',
    }

    point_not_null_attrs = [
        'title',
        'latitude',
        'longitude',
        'unlisted',
    ]


class PointCreationTestCase(PointGenericMixin, MultipleUsersTestMixin, TestCase):
    def test_point_creation(self):
        data = self.point_data
        response = self.alice_client.post(self.point_create_path, data=data)
        self.assertEqual(response.status_code, 201)
        response_data = response.json()

        for k, v in data.items():
            self.assertEqual(response_data[k], data[k], msg='invalid value for attribute "{}"'.format(k))

        self.assertIn('id', response_data)

    def test_zero_coordinates(self):
        data = copy(self.point_data)
        data.update({
            'latitude': 0,
            'longitude': 0,
        })

        response = self.alice_client.post(self.point_create_path, data=data)
        self.assertEqual(response.status_code, 201)

    def test_required_fields(self):
        response = self.alice_client.post(self.point_create_path, data={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json().keys()), set(self.point_data.keys()))

    def test_empty_fields(self):
        data = copy(self.point_data)
        data.update(self.point_empty_data)
        response = self.alice_client.post(self.point_create_path, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json().keys()), set(self.point_empty_data.keys()))

    def test_null_fields(self):
        data = copy(self.point_data)
        for k in self.point_not_null_attrs:
            data[k] = None

        response = self.alice_client.post(self.point_create_path, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json().keys()), set(self.point_not_null_attrs))

    def test_max_values(self):
        overhead_data = {
            'title': '1'*101,
        }
        data = copy(self.point_data)
        data.update(overhead_data)
        response = self.alice_client.post(self.point_create_path, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json().keys()), set(overhead_data.keys()))

    def test_anonymous(self):
        data = self.point_data
        response = self.client.post(self.point_create_path, data=data)
        self.assertEqual(response.status_code, 401)

    def test_options(self):
        for method in ['GET', 'POST']:
            response = self.client.options(self.point_create_path, HTTP_ACCESS_CONTROL_REQUEST_METHOD=method)
            self.assertEqual(response.status_code, 200, msg='for {}'.format(method))


class CreatePointMixin:
    def setUp(self):
        super().setUp()
        response = self.alice_client.post(self.point_create_path, data=self.point_data)
        self.assertEqual(response.status_code, 201)
        self.point = response.json()


class ModeratorsMixin:
    usernames = ['alice', 'bob', 'carol', 'dave', 'eve', 'faythe']

    def setUp(self):
        super().setUp()
        perm = Permission.objects.get(codename='change_point')

        carol = User.objects.get(email=self.profiles['carol']['email'])
        carol.is_staff = True
        carol.save()
        carol.user_permissions.add(perm)

        dave = User.objects.get(email=self.profiles['dave']['email'])
        dave.is_staff = True
        dave.save()

        eve = User.objects.get(email=self.profiles['eve']['email'])
        eve.user_permissions.add(perm)

        faythe = User.objects.get(email=self.profiles['faythe']['email'])
        faythe.is_superuser = True
        faythe.save()


class PointDetailTestCase(CreatePointMixin, ModeratorsMixin, PointGenericMixin, MultipleUsersTestMixin, TestCase):
    update_data = {
        'title': 'Updated point',
        'latitude': 59.89,
        'longitude': 30.34,
        'unlisted': True,
    }

    def get_details(self, client, expected_data):
        response = client.get(self.point_detail_path.format(id=self.point['id']))
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data, expected_data)

    def update(self, client):
        path = self.point_detail_path.format(id=self.point['id'])
        data = copy(self.point_data)
        data.update(self.update_data)

        expected_data = copy(self.point)
        expected_data.update(self.update_data)

        response = client.put(path, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

    def destroy(self, client):
        path = self.point_detail_path.format(id=self.point['id'])

        response = client.delete(path)
        self.assertEqual(response.status_code, 204)

        response = client.get(path)
        self.assertEqual(response.status_code, 404)

    def test_retrieve(self):
        self.get_details(self.alice_client, self.point)

    def test_other_users_retrieve(self):
        expected_data = copy(self.point)

        self.get_details(self.carol_client, expected_data)
        self.get_details(self.faythe_client, expected_data)

        expected_data['can_edit'] = False

        self.get_details(self.bob_client, expected_data)
        self.get_details(self.dave_client, expected_data)
        self.get_details(self.eve_client, expected_data)
        self.get_details(self.client, expected_data)

    def test_update(self):
        self.update(self.alice_client)
        self.update(self.carol_client)
        self.update(self.faythe_client)

    def test_other_users_update(self):
        path = self.point_detail_path.format(id=self.point['id'])

        response = self.client.put(path, self.point_data)
        self.assertEqual(response.status_code, 401)

        response = self.bob_client.put(path, self.point_data)
        self.assertEqual(response.status_code, 403)

        response = self.dave_client.put(path, self.point_data)
        self.assertEqual(response.status_code, 403)

        response = self.eve_client.put(path, self.point_data)
        self.assertEqual(response.status_code, 403)

    def test_required_fields(self):
        path = self.point_detail_path.format(id=self.point['id'])
        response = self.alice_client.put(path, data={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json().keys()), set(self.point_data.keys()))

    def test_empty_fields(self):
        path = self.point_detail_path.format(id=self.point['id'])
        data = copy(self.point_data)
        data.update(self.point_empty_data)
        response = self.alice_client.put(path, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json().keys()), set(self.point_empty_data.keys()))

    def test_null_fields(self):
        path = self.point_detail_path.format(id=self.point['id'])
        data = copy(self.point_data)
        for k in self.point_not_null_attrs:
            data[k] = None

        response = self.alice_client.put(path, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json().keys()), set(self.point_not_null_attrs))

    def test_destroy(self):
        self.destroy(self.alice_client)

        path = self.point_detail_path.format(id=self.point['id'])
        response = self.alice_client.delete(path)
        self.assertEqual(response.status_code, 404)

    def test_moderator_destroy(self):
        self.destroy(self.carol_client)

    def test_superuser_destroy(self):
        self.destroy(self.faythe_client)

    def test_other_users_destroy(self):
        path = self.point_detail_path.format(id=self.point['id'])

        response = self.client.delete(path)
        self.assertEqual(response.status_code, 401)

        response = self.bob_client.delete(path)
        self.assertEqual(response.status_code, 403)

        response = self.dave_client.delete(path)
        self.assertEqual(response.status_code, 403)

        response = self.eve_client.delete(path)
        self.assertEqual(response.status_code, 403)


class PointUndeleteTestCase(CreatePointMixin, ModeratorsMixin, PointGenericMixin, MultipleUsersTestMixin, TestCase):
    def setUp(self):
        super().setUp()

        path = self.point_detail_path.format(id=self.point['id'])
        response = self.alice_client.delete(path)
        self.assertEqual(response.status_code, 204)

    def undelete(self, client):
        path = self.point_undelete_path.format(id=self.point['id'])
        response = client.delete(path)
        self.assertEqual(response.status_code, 204)

        response = self.alice_client.get(self.point_detail_path.format(id=self.point['id']))
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data, self.point)

    def test_owner_undelete(self):
        self.undelete(self.alice_client)

        path = self.point_undelete_path.format(id=self.point['id'])
        response = self.alice_client.delete(path)
        self.assertEqual(response.status_code, 404)

    def test_moderator_undelete(self):
        self.undelete(self.carol_client)

    def test_superuser_undelete(self):
        self.undelete(self.faythe_client)

    def test_other_users_undelete(self):
        path = self.point_undelete_path.format(id=self.point['id'])

        response = self.client.delete(path)
        self.assertEqual(response.status_code, 401)

        response = self.bob_client.delete(path)
        self.assertEqual(response.status_code, 403)

        response = self.dave_client.delete(path)
        self.assertEqual(response.status_code, 403)

        response = self.eve_client.delete(path)
        self.assertEqual(response.status_code, 403)


class PointListTestCase(CreatePointMixin, ModeratorsMixin, PointGenericMixin, MultipleUsersTestMixin, TestCase):
    def setUp(self):
        super().setUp()

        data = copy(self.point_data)
        data['unlisted'] = True
        response = self.alice_client.post(self.point_create_path, data=data)
        self.assertEqual(response.status_code, 201)

    def check_list(self, client, expected_data, query_params=None):
        response = client.get(self.point_list_path, query_params)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIsInstance(response_data, list)
        self.assertEqual(response_data, expected_data)

    def test_list(self):
        expected_data = [copy(self.point)]
        self.check_list(self.alice_client, expected_data)
        self.check_list(self.carol_client, expected_data)
        self.check_list(self.faythe_client, expected_data)

        expected_data[0]['can_edit'] = False

        self.check_list(self.bob_client, expected_data)
        self.check_list(self.dave_client, expected_data)
        self.check_list(self.eve_client, expected_data)
        self.check_list(self.client, expected_data)

    def check_list_filters(self):
        self.check_list(self.alice_client, [self.point], {'geo': '59.878,30.321,10000'})
        self.check_list(self.alice_client, [], {'geo': '59.878,30.321,100'})
