from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from .models import AIInteraction, Traveler, Trip, Recommendation
from django.utils import timezone


class DashboardOverviewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create test users
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')
        
        # Traveler profiles should be auto-created via signals
        self.traveler1, _ = Traveler.objects.get_or_create(user=self.user1)
        self.traveler2, _ = Traveler.objects.get_or_create(user=self.user2)

    def test_dashboard_requires_authentication(self):
        """Test that dashboard endpoint requires JWT authentication."""
        r = self.client.get('/api/dashboard/overview/')
        self.assertEqual(r.status_code, 401)

    def test_dashboard_returns_user_data(self):
        """Test that dashboard returns correct user-specific data."""
        self.client.force_authenticate(user=self.user1)
        r = self.client.get('/api/dashboard/overview/')
        self.assertEqual(r.status_code, 200)
        
        data = r.json()
        self.assertEqual(data['username'], 'user1')
        self.assertEqual(data['total_trips'], 0)  # No trips yet
        self.assertEqual(data['ai_interactions'], 0)  # No interactions yet
        self.assertIn('member_since', data)

    def test_dashboard_counts_user_trips(self):
        """Test that dashboard correctly counts user's trips."""
        # Create some recommendations
        rec1 = Recommendation.objects.create(city='Paris', name='Eiffel Tower')
        rec2 = Recommendation.objects.create(city='London', name='Big Ben')
        
        # Create trips for user1
        trip1 = Trip.objects.create(
            traveler=self.traveler1,
            title='Trip 1',
            start_date='2026-01-01',
            end_date='2026-01-05'
        )
        trip1.recommendations.add(rec1)
        
        trip2 = Trip.objects.create(
            traveler=self.traveler1,
            title='Trip 2',
            start_date='2026-02-01',
            end_date='2026-02-10'
        )
        trip2.recommendations.add(rec2)
        
        # Create trip for user2 (should not be counted for user1)
        trip3 = Trip.objects.create(
            traveler=self.traveler2,
            title='Trip 3',
            start_date='2026-03-01',
            end_date='2026-03-05'
        )
        
        # Check dashboard for user1
        self.client.force_authenticate(user=self.user1)
        r = self.client.get('/api/dashboard/overview/')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data['total_trips'], 2)
        
        # Check dashboard for user2
        self.client.force_authenticate(user=self.user2)
        r2 = self.client.get('/api/dashboard/overview/')
        self.assertEqual(r2.status_code, 200)
        data2 = r2.json()
        self.assertEqual(data2['total_trips'], 1)

    def test_dashboard_counts_ai_interactions(self):
        """Test that dashboard correctly counts AI interactions."""
        # Create AI interactions for user1
        AIInteraction.objects.create(
            user=self.user1,
            prompt='Plan a trip to Paris',
            ai_response='Here is a plan...'
        )
        AIInteraction.objects.create(
            user=self.user1,
            prompt='What about London?',
            ai_response='London is great...'
        )
        
        # Create interaction for user2
        AIInteraction.objects.create(
            user=self.user2,
            prompt='Describe Tokyo',
            ai_response='Tokyo is amazing...'
        )
        
        # Check dashboard for user1
        self.client.force_authenticate(user=self.user1)
        r = self.client.get('/api/dashboard/overview/')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data['ai_interactions'], 2)
        
        # Check dashboard for user2
        self.client.force_authenticate(user=self.user2)
        r2 = self.client.get('/api/dashboard/overview/')
        self.assertEqual(r2.status_code, 200)
        data2 = r2.json()
        self.assertEqual(data2['ai_interactions'], 1)

    def test_dashboard_aggregates_all_data(self):
        """Test that dashboard correctly aggregates trips and interactions together."""
        # Create recommendations
        rec1 = Recommendation.objects.create(city='Paris', name='Eiffel Tower')
        
        # Create 3 trips for user1
        for i in range(3):
            trip = Trip.objects.create(
                traveler=self.traveler1,
                title=f'Trip {i+1}',
                start_date='2026-01-01',
                end_date='2026-01-05'
            )
            trip.recommendations.add(rec1)
        
        # Create 5 AI interactions for user1
        for i in range(5):
            AIInteraction.objects.create(
                user=self.user1,
                prompt=f'Query {i+1}',
                ai_response=f'Response {i+1}'
            )
        
        self.client.force_authenticate(user=self.user1)
        r = self.client.get('/api/dashboard/overview/')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        
        self.assertEqual(data['username'], 'user1')
        self.assertEqual(data['total_trips'], 3)
        self.assertEqual(data['ai_interactions'], 5)
        self.assertIn('member_since', data)

    def test_dashboard_member_since_is_user_date_joined(self):
        """Test that member_since matches user.date_joined."""
        self.client.force_authenticate(user=self.user1)
        r = self.client.get('/api/dashboard/overview/')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        
        # member_since should be a datetime string; check that it exists and is ISO format
        self.assertIn('member_since', data)
        self.assertIsInstance(data['member_since'], str)
        # Verify it matches the user's date_joined by comparing the date part
        from django.utils.dateparse import parse_datetime
        returned_datetime = parse_datetime(data['member_since'])
        self.assertEqual(returned_datetime.date(), self.user1.date_joined.date())

    def test_dashboard_user_isolation(self):
        """Test that users can only see their own dashboard data."""
        # Create data for both users
        rec1 = Recommendation.objects.create(city='Paris', name='Eiffel Tower')
        trip1 = Trip.objects.create(traveler=self.traveler1, title='Trip 1', start_date='2026-01-01', end_date='2026-01-05')
        trip1.recommendations.add(rec1)
        AIInteraction.objects.create(user=self.user1, prompt='Test', ai_response='Response')
        
        # Create 3 trips for user2 (different from user1's 1 trip)
        for i in range(3):
            trip = Trip.objects.create(traveler=self.traveler2, title=f'Trip {i+2}', start_date='2026-02-01', end_date='2026-02-05')
            trip.recommendations.add(rec1)
        
        for i in range(3):
            AIInteraction.objects.create(user=self.user2, prompt=f'Query {i}', ai_response=f'Resp {i}')
        
        # Check user1's dashboard
        self.client.force_authenticate(user=self.user1)
        r1 = self.client.get('/api/dashboard/overview/')
        data1 = r1.json()
        self.assertEqual(data1['total_trips'], 1)
        self.assertEqual(data1['ai_interactions'], 1)
        
        # Check user2's dashboard
        self.client.force_authenticate(user=self.user2)
        r2 = self.client.get('/api/dashboard/overview/')
        data2 = r2.json()
        self.assertEqual(data2['total_trips'], 3)
        self.assertEqual(data2['ai_interactions'], 3)
        
        # Data should be different
        self.assertNotEqual(data1['total_trips'], data2['total_trips'])
        self.assertNotEqual(data1['ai_interactions'], data2['ai_interactions'])

    def test_dashboard_returns_json_response(self):
        """Test that dashboard returns proper JSON response with all required fields."""
        self.client.force_authenticate(user=self.user1)
        r = self.client.get('/api/dashboard/overview/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'application/json')
        
        data = r.json()
        required_fields = ['username', 'total_trips', 'ai_interactions', 'member_since']
        for field in required_fields:
            self.assertIn(field, data)

    def test_dashboard_readonly_no_post_allowed(self):
        """Test that dashboard endpoint only accepts GET requests."""
        self.client.force_authenticate(user=self.user1)
        
        # POST should not be allowed
        r = self.client.post('/api/dashboard/overview/', {}, format='json')
        self.assertEqual(r.status_code, 405)  # Method Not Allowed
        
        # PUT should not be allowed
        r2 = self.client.put('/api/dashboard/overview/', {}, format='json')
        self.assertEqual(r2.status_code, 405)
        
        # DELETE should not be allowed
        r3 = self.client.delete('/api/dashboard/overview/')
        self.assertEqual(r3.status_code, 405)
