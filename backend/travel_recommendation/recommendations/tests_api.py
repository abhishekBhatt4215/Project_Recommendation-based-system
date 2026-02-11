from django.test import TestCase
from rest_framework.test import APIClient
from .models import Recommendation , Guide
from django.urls import reverse


class RecommendationAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create sample recommendations
        for i in range(1, 6):
            Recommendation.objects.create(city=f"City{i}", name=f"Place{i}", ratings=i * 1.0, popularity=i * 0.1)

    def test_list_recommendations(self):
        r = self.client.get('/api/recommendations/')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('results', data)
        self.assertGreaterEqual(len(data['results']), 5)

    def test_create_recommendation_requires_admin(self):
        payload = {'city': 'New City', 'name': 'New Place', 'ratings': 4.2}
        # anonymous should not be able to create
        r = self.client.post('/api/recommendations/', payload, format='json')
        self.assertIn(r.status_code, (401, 403))

        # admin can create
        from django.contrib.auth.models import User
        admin = User.objects.create_superuser(username='admin', email='admin@example.com', password='adminpass')
        self.client.force_authenticate(user=admin)
        r2 = self.client.post('/api/recommendations/', payload, format='json')
        self.assertEqual(r2.status_code, 201)
        self.assertTrue(Recommendation.objects.filter(city='New City').exists())

    def test_retrieve_update_delete_requires_admin_for_writes(self):
        rec = Recommendation.objects.first()
        r = self.client.get(f'/api/recommendations/{rec.pk}/')
        self.assertEqual(r.status_code, 200)
        # anonymous update should be blocked
        r2 = self.client.patch(f'/api/recommendations/{rec.pk}/', {'name': 'Updated'}, format='json')
        self.assertIn(r2.status_code, (401, 403))
        rec.refresh_from_db()
        self.assertNotEqual(rec.name, 'Updated')
        # anonymous delete should be blocked
        r3 = self.client.delete(f'/api/recommendations/{rec.pk}/')
        self.assertIn(r3.status_code, (401, 403))
        self.assertTrue(Recommendation.objects.filter(pk=rec.pk).exists())

        # admin can update and delete
        from django.contrib.auth.models import User
        admin = User.objects.create_superuser(username='admin2', email='admin2@example.com', password='adminpass')
        self.client.force_authenticate(user=admin)
        r4 = self.client.patch(f'/api/recommendations/{rec.pk}/', {'name': 'UpdatedByAdmin'}, format='json')
        self.assertEqual(r4.status_code, 200)
        rec.refresh_from_db()
        self.assertEqual(rec.name, 'UpdatedByAdmin')
        r5 = self.client.delete(f'/api/recommendations/{rec.pk}/')
        self.assertEqual(r5.status_code, 204)
        self.assertFalse(Recommendation.objects.filter(pk=rec.pk).exists())

    def test_filtering_and_ordering(self):
        r = self.client.get('/api/recommendations/?city=City1')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(len(data['results']), 1)

        r2 = self.client.get('/api/recommendations/?ordering=-ratings')
        self.assertEqual(r2.status_code, 200)
        data2 = r2.json()
        ratings = [item['ratings'] for item in data2['results']]
        self.assertEqual(ratings[0], 5.0)

    def test_pagination(self):
        # create more to exceed default page size (PAGE_SIZE=20)
        for i in range(6, 27):
            Recommendation.objects.create(city=f"Bulk{i}")
        r = self.client.get('/api/recommendations/')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(len(data['results']), 20)
        self.assertIsNotNone(data.get('next'))


class GuideAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        Guide.objects.create(name='G1', city='City1')

    def test_list_and_create_guide(self):
        r = self.client.get('/api/guides/')
        self.assertEqual(r.status_code, 200)
        self.assertGreaterEqual(len(r.json()['results']), 1)

        payload = {'name': 'G2', 'city': 'City2'}
        r2 = self.client.post('/api/guides/', payload, format='json')
        self.assertEqual(r2.status_code, 201)
        from .models import Guide
        self.assertTrue(Guide.objects.filter(name='G2').exists())

    def test_retrieve_update_delete_guide(self):
        from .models import Guide
        g = Guide.objects.first()
        r = self.client.get(f'/api/guides/{g.pk}/')
        self.assertEqual(r.status_code, 200)

        r2 = self.client.patch(f'/api/guides/{g.pk}/', {'bio': 'Updated bio'}, format='json')
        self.assertEqual(r2.status_code, 200)
        g.refresh_from_db()
        self.assertEqual(g.bio, 'Updated bio')

        r3 = self.client.delete(f'/api/guides/{g.pk}/')
        self.assertEqual(r3.status_code, 204)
        self.assertFalse(Guide.objects.filter(pk=g.pk).exists())


class TravelerTripAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        from django.contrib.auth.models import User
        from .models import Traveler, Recommendation
        # Create user and traveler
        user = User.objects.create_user(username='testuser', password='pass')
        self.user = user
        # signals auto-create a Traveler on user creation; use get_or_create to avoid duplicates
        self.traveler, _ = Traveler.objects.get_or_create(user=user, defaults={'bio': 'hello'})
        # Create recommendations
        self.r1 = Recommendation.objects.create(city='CityA', name='PlaceA')
        self.r2 = Recommendation.objects.create(city='CityB', name='PlaceB')

    def test_create_and_manage_trip(self):
        payload = {
            'traveler': self.traveler.pk,
            'title': 'My Trip',
            'start_date': '2026-01-01',
            'end_date': '2026-01-05',
            'recommendations': [self.r1.pk, self.r2.pk]
        }
        # authenticate as the owner user (tests assume authenticated users create trips)
        self.client.force_authenticate(user=self.user)
        r = self.client.post('/api/trips/', payload, format='json')
        self.assertEqual(r.status_code, 201)
        data = r.json()
        self.assertIn('id', data)
        trip_id = data['id']

        # retrieve
        r2 = self.client.get(f'/api/trips/{trip_id}/')
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.json()['title'], 'My Trip')

        # update
        r3 = self.client.patch(f'/api/trips/{trip_id}/', {'title': 'New Title'}, format='json')
        self.assertEqual(r3.status_code, 200)
        self.assertEqual(r3.json()['title'], 'New Title')

        # delete
        r4 = self.client.delete(f'/api/trips/{trip_id}/')
        self.assertEqual(r4.status_code, 204)
        from .models import Trip
        self.assertFalse(Trip.objects.filter(pk=trip_id).exists())

