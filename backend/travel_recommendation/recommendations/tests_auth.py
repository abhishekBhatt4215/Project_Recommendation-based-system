from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from .models import Traveler


class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_and_login_and_protected_endpoints(self):
        # register
        r = self.client.post('/api/auth/register/', {'username': 'u1', 'email': 'u1@example.com', 'password': 'Passw0rd!'}, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertTrue(User.objects.filter(username='u1').exists())

        # login (token obtain)
        r2 = self.client.post('/api/auth/token/', {'username': 'u1', 'password': 'Passw0rd!'}, format='json')
        self.assertEqual(r2.status_code, 200)
        tokens = r2.json()
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
        access = tokens['access']

        # After registration a Traveler profile should exist automatically
        user = User.objects.get(username='u1')
        self.assertTrue(Traveler.objects.filter(user=user).exists())
        tr = Traveler.objects.get(user=user)

        # access traveler detail without token -> 401
        r3 = self.client.get(f'/api/travelers/{tr.pk}/')
        self.assertEqual(r3.status_code, 401)

        # access with token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        r4 = self.client.get(f'/api/travelers/{tr.pk}/')
        self.assertEqual(r4.status_code, 200)

        # clients should NOT be able to create Traveler via API
        r5 = self.client.post('/api/travelers/', {'bio': 'should not create'}, format='json')
        self.assertEqual(r5.status_code, 405)
    def test_trip_requires_auth(self):
        # create user and traveler
        u = User.objects.create_user(username='u2', password='pass2')
        tr, _ = Traveler.objects.get_or_create(user=u)

        # no token -> 401 or 403 (depends on auth flow)
        r = self.client.post('/api/trips/', {'traveler': tr.pk, 'title': 'T', 'start_date': '2026-01-01', 'end_date': '2026-01-04'}, format='json')
        self.assertIn(r.status_code, (401, 403))

        # get token
        r2 = self.client.post('/api/auth/token/', {'username': 'u2', 'password': 'pass2'}, format='json')
        access = r2.json()['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

        r3 = self.client.post('/api/trips/', {'traveler': tr.pk, 'title': 'T', 'start_date': '2026-01-01', 'end_date': '2026-01-04'}, format='json')
        self.assertEqual(r3.status_code, 201)
