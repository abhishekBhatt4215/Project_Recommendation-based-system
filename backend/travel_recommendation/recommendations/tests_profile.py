from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from .models import Traveler
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone


class ProfileMeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create test users
        self.user1 = User.objects.create_user(username='user1', email='user1@test.com', password='pass1')
        self.user2 = User.objects.create_user(username='user2', email='user2@test.com', password='pass2')
        
        # Traveler profiles auto-created via signals
        self.traveler1, _ = Traveler.objects.get_or_create(user=self.user1)
        self.traveler2, _ = Traveler.objects.get_or_create(user=self.user2)

    def test_profile_me_requires_authentication(self):
        """Test that profile endpoint requires JWT authentication."""
        r = self.client.get('/api/profile/me/')
        self.assertEqual(r.status_code, 401)

    def test_profile_me_get_returns_user_info(self):
        """Test that GET returns user's own profile info."""
        self.client.force_authenticate(user=self.user1)
        r = self.client.get('/api/profile/me/')
        self.assertEqual(r.status_code, 200)
        
        data = r.json()
        self.assertEqual(data['username'], 'user1')
        self.assertEqual(data['email'], 'user1@test.com')
        self.assertIn('joined_on', data)

    def test_profile_me_get_returns_traveler_data(self):
        """Test that GET returns traveler profile data."""
        # Update traveler with profile data
        self.traveler1.bio = 'I love traveling'
        self.traveler1.interests = 'hiking, museums, food'
        self.traveler1.travel_style = 'adventure'
        self.traveler1.save()
        
        self.client.force_authenticate(user=self.user1)
        r = self.client.get('/api/profile/me/')
        self.assertEqual(r.status_code, 200)
        
        data = r.json()
        self.assertEqual(data['bio'], 'I love traveling')
        self.assertEqual(data['interests'], 'hiking, museums, food')
        self.assertEqual(data['travel_style'], 'adventure')

    def test_profile_me_get_returns_profile_image_url(self):
        """Test that GET returns profile image as absolute URL."""
        self.client.force_authenticate(user=self.user1)
        r = self.client.get('/api/profile/me/')
        self.assertEqual(r.status_code, 200)
        
        data = r.json()
        self.assertIn('profile_image', data)
        # Should be None since no image set
        self.assertIsNone(data['profile_image'])

    def test_profile_me_put_updates_traveler_profile(self):
        """Test that PUT updates user's own traveler profile."""
        self.client.force_authenticate(user=self.user1)
        
        payload = {
            'bio': 'Updated bio',
            'interests': 'photography, cooking',
            'travel_style': 'luxury'
        }
        r = self.client.put('/api/profile/me/', payload, format='json')
        self.assertEqual(r.status_code, 200)
        
        data = r.json()
        self.assertEqual(data['bio'], 'Updated bio')
        self.assertEqual(data['interests'], 'photography, cooking')
        self.assertEqual(data['travel_style'], 'luxury')
        
        # Verify changes persisted
        self.traveler1.refresh_from_db()
        self.assertEqual(self.traveler1.bio, 'Updated bio')
        self.assertEqual(self.traveler1.interests, 'photography, cooking')
        self.assertEqual(self.traveler1.travel_style, 'luxury')

    def test_profile_me_put_partial_updates(self):
        """Test that PUT allows partial updates (only some fields)."""
        self.traveler1.bio = 'Original bio'
        self.traveler1.interests = 'Original interests'
        self.traveler1.save()
        
        self.client.force_authenticate(user=self.user1)
        
        # Update only bio
        payload = {'bio': 'New bio only'}
        r = self.client.put('/api/profile/me/', payload, format='json')
        self.assertEqual(r.status_code, 200)
        
        data = r.json()
        self.assertEqual(data['bio'], 'New bio only')
        self.assertEqual(data['interests'], 'Original interests')  # Should remain unchanged

    def test_profile_me_cannot_update_user_fields(self):
        """Test that users cannot update username or email via profile endpoint."""
        self.client.force_authenticate(user=self.user1)
        
        # Attempt to update username/email (these should be ignored as read-only)
        payload = {
            'username': 'hacker',
            'email': 'hacker@test.com',
            'bio': 'My bio'
        }
        r = self.client.put('/api/profile/me/', payload, format='json')
        self.assertEqual(r.status_code, 200)
        
        # Verify username and email didn't change
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.username, 'user1')
        self.assertEqual(self.user1.email, 'user1@test.com')
        
        # But bio should be updated
        self.traveler1.refresh_from_db()
        self.assertEqual(self.traveler1.bio, 'My bio')

    def test_profile_me_user_isolation_get(self):
        """Test that user1 cannot see user2's profile via GET."""
        self.traveler2.bio = 'User2 secret bio'
        self.traveler2.save()
        
        self.client.force_authenticate(user=self.user1)
        r = self.client.get('/api/profile/me/')
        self.assertEqual(r.status_code, 200)
        
        data = r.json()
        # Should see user1's profile, not user2's
        self.assertEqual(data['username'], 'user1')
        self.assertNotEqual(data['bio'], 'User2 secret bio')

    def test_profile_me_user_isolation_put(self):
        """Test that users can only update their own profile."""
        self.traveler1.bio = 'User1 bio'
        self.traveler1.save()
        
        self.client.force_authenticate(user=self.user1)
        
        # Try to update (but endpoint only allows updating own profile)
        payload = {'bio': 'Updated user1 bio'}
        r = self.client.put('/api/profile/me/', payload, format='json')
        self.assertEqual(r.status_code, 200)
        
        # User1's profile should be updated
        self.traveler1.refresh_from_db()
        self.assertEqual(self.traveler1.bio, 'Updated user1 bio')
        
        # User2's profile should remain unchanged
        self.traveler2.refresh_from_db()
        self.assertNotEqual(self.traveler2.bio, 'Updated user1 bio')

    def test_profile_me_joined_on_is_readonly(self):
        """Test that joined_on field is read-only and matches user.date_joined."""
        self.client.force_authenticate(user=self.user1)
        r = self.client.get('/api/profile/me/')
        self.assertEqual(r.status_code, 200)
        
        data = r.json()
        self.assertIn('joined_on', data)
        
        # Verify it can't be updated
        payload = {'joined_on': '2020-01-01T00:00:00Z'}
        r2 = self.client.put('/api/profile/me/', payload, format='json')
        self.assertEqual(r2.status_code, 200)
        
        # joined_on should remain unchanged
        data2 = r2.json()
        self.assertEqual(data2['joined_on'], data['joined_on'])

    def test_profile_me_profile_image_is_readonly(self):
        """Test that profile_image field is read-only."""
        self.client.force_authenticate(user=self.user1)
        
        # Try to update profile_image (should be ignored)
        payload = {
            'profile_image': 'http://fake.com/image.jpg',
            'bio': 'Updated bio'
        }
        r = self.client.put('/api/profile/me/', payload, format='json')
        self.assertEqual(r.status_code, 200)
        
        data = r.json()
        self.assertIsNone(data['profile_image'])  # Should still be None
        self.assertEqual(data['bio'], 'Updated bio')  # But bio should update

    def test_profile_me_returns_json_response(self):
        """Test that endpoint returns proper JSON response."""
        self.client.force_authenticate(user=self.user1)
        r = self.client.get('/api/profile/me/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'application/json')
        
        data = r.json()
        required_fields = ['username', 'email', 'joined_on', 'bio', 'profile_image', 'interests', 'travel_style']
        for field in required_fields:
            self.assertIn(field, data)

    def test_profile_me_put_with_empty_fields(self):
        """Test that PUT can clear/empty fields."""
        self.traveler1.bio = 'Original bio'
        self.traveler1.interests = 'Original interests'
        self.traveler1.travel_style = 'Original style'
        self.traveler1.save()
        
        self.client.force_authenticate(user=self.user1)
        
        # Clear bio by sending empty string
        payload = {'bio': ''}
        r = self.client.put('/api/profile/me/', payload, format='json')
        self.assertEqual(r.status_code, 200)
        
        self.traveler1.refresh_from_db()
        self.assertEqual(self.traveler1.bio, '')

    def test_profile_me_post_not_allowed(self):
        """Test that POST method is not allowed."""
        self.client.force_authenticate(user=self.user1)
        r = self.client.post('/api/profile/me/', {}, format='json')
        self.assertEqual(r.status_code, 405)  # Method Not Allowed

    def test_profile_me_delete_not_allowed(self):
        """Test that DELETE method is not allowed."""
        self.client.force_authenticate(user=self.user1)
        r = self.client.delete('/api/profile/me/')
        self.assertEqual(r.status_code, 405)  # Method Not Allowed
