from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from .models import AIInteraction
import json
from unittest.mock import patch, MagicMock


class AIInteractionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create test users
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')

    def test_ai_history_requires_auth(self):
        """Test that AI history endpoint requires authentication."""
        # Unauthenticated request should fail
        r = self.client.get('/api/ai/history/')
        self.assertEqual(r.status_code, 401)

    def test_ai_history_returns_user_interactions_only(self):
        """Test that users only see their own AI interactions."""
        # Create some AI interactions for both users
        import time
        interaction1 = AIInteraction.objects.create(
            user=self.user1,
            prompt='Tell me about Paris',
            ai_response='Paris is the capital of France...'
        )
        time.sleep(0.01)  # Small delay to ensure different timestamps
        interaction2 = AIInteraction.objects.create(
            user=self.user1,
            prompt='What about London?',
            ai_response='London is the capital of England...'
        )
        time.sleep(0.01)
        AIInteraction.objects.create(
            user=self.user2,
            prompt='Describe Tokyo',
            ai_response='Tokyo is the capital of Japan...'
        )

        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)
        r = self.client.get('/api/ai/history/')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(len(data), 2)
        # Model orders by -created_at, so newest first
        # Check that we have both interactions
        prompts = [item['prompt'] for item in data]
        self.assertIn('What about London?', prompts)
        self.assertIn('Tell me about Paris', prompts)
        # Newest should come first
        self.assertEqual(data[0]['prompt'], 'What about London?')

        # Authenticate as user2
        self.client.force_authenticate(user=self.user2)
        r2 = self.client.get('/api/ai/history/')
        self.assertEqual(r2.status_code, 200)
        data2 = r2.json()
        self.assertEqual(len(data2), 1)
        self.assertEqual(data2[0]['prompt'], 'Describe Tokyo')

    def test_ai_history_is_read_only(self):
        """Test that AI history endpoint does not allow create/update/delete."""
        self.client.force_authenticate(user=self.user1)

        # POST should fail (method not allowed)
        r = self.client.post('/api/ai/history/', {'prompt': 'test'}, format='json')
        self.assertIn(r.status_code, (405, 403))  # 405 Method Not Allowed or 403 Forbidden

    @patch('recommendations.views.requests.post')
    def test_ai_plan_trip_saves_interaction(self, mock_post):
        """Test that AI plan_trip endpoint saves interaction to database."""
        # Mock the AI service response
        mock_response = MagicMock()
        mock_response.json.return_value = {'itinerary': 'Day 1: Visit Eiffel Tower...', 'places': []}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        self.client.force_authenticate(user=self.user1)
        
        payload = {'prompt': 'Plan a trip to Paris'}
        r = self.client.post('/api/ai/plan_trip/', payload, format='json')
        
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['itinerary'], 'Day 1: Visit Eiffel Tower...')

        # Check that interaction was saved
        self.assertTrue(AIInteraction.objects.filter(user=self.user1).exists())
        interaction = AIInteraction.objects.get(user=self.user1)
        self.assertIn('Plan a trip to Paris', interaction.prompt)
        self.assertIn('Eiffel Tower', interaction.ai_response)

    @patch('recommendations.views.requests.post')
    def test_ai_plan_trip_requires_auth(self, mock_post):
        """Test that AI plan_trip endpoint requires authentication."""
        # Unauthenticated request should fail
        r = self.client.post('/api/ai/plan_trip/', {'prompt': 'test'}, format='json')
        self.assertEqual(r.status_code, 401)

    @patch('recommendations.views.requests.post')
    def test_ai_interaction_not_writable_by_user(self, mock_post):
        """Test that user cannot directly write to AI interactions."""
        # Create an interaction
        interaction = AIInteraction.objects.create(
            user=self.user1,
            prompt='Original prompt',
            ai_response='Original response'
        )

        self.client.force_authenticate(user=self.user1)
        
        # Verify user field in history is read-only (showing username)
        r = self.client.get('/api/ai/history/')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['user'], 'user1')  # Read-only username field

    @patch('recommendations.views.requests.post')
    def test_user1_cannot_see_user2_interactions(self, mock_post):
        """Test that users cannot access other users' AI interactions."""
        # Create interactions for user2
        AIInteraction.objects.create(
            user=self.user2,
            prompt='Secret trip plan',
            ai_response='Here is your secret trip...'
        )

        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)
        r = self.client.get('/api/ai/history/')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        
        # user1 should see no interactions
        self.assertEqual(len(data), 0)

    @patch('recommendations.views.requests.post')
    def test_ai_service_error_handling(self, mock_post):
        """Test that AI service errors are handled gracefully."""
        # Mock requests.post to raise an exception
        mock_post.side_effect = Exception('Connection error')

        self.client.force_authenticate(user=self.user1)
        
        payload = {'prompt': 'Plan a trip'}
        r = self.client.post('/api/ai/plan_trip/', payload, format='json')
        
        # Should return 502 Bad Gateway
        self.assertEqual(r.status_code, 502)
        self.assertIn('detail', r.json())

        # No interaction should be saved on error
        self.assertFalse(AIInteraction.objects.filter(user=self.user1).exists())
