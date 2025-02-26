import os
import tempfile
from PIL import Image
from django.core.files.storage import default_storage
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Profile

# URL Constants
PROFILE_URL = reverse("profilee:me")
LIKE_URL = lambda profile_id: reverse("profilee:like-profile", args=[profile_id])
TOP_LIKED_URL = reverse("profilee:top-liked-profiles")


def create_user(**params):
    """
    Helper function to create a new user.
    """
    return get_user_model().objects.create_user(**params)


class PublicProfileAPITests(TestCase):
    """
    Tests for profile API that do NOT require authentication.
    """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required to access the profile."""
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateProfileAPITests(TestCase):
    """
    Tests for profile API that REQUIRE authentication.
    """

    def setUp(self):
        self.user = create_user(email="test@example.com", password="testpass123", name="Test Name")
        self.profile = Profile.objects.create(user=self.user, status="single")

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving the profile of the authenticated user."""
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["status"], self.profile.status)

    def test_update_profile(self):
        """Test updating the status field of the user's profile."""
        payload = {"status": "married"}
        res = self.client.patch(PROFILE_URL, payload)
        self.profile.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.profile.status, payload["status"])

    def test_profile_auto_created_on_user_creation(self):
        """Test that a profile is NOT automatically created when a new user is registered."""
        new_user = create_user(email="newuser@example.com", password="testpass123")
        profile_exists = Profile.objects.filter(user=new_user).exists()
        self.assertFalse(profile_exists)

    def test_update_profile_image(self):
        """Test uploading a profile image."""
        with tempfile.NamedTemporaryFile(suffix=".jpg") as temp_image:
            image = Image.new("RGB", (100, 100), color="blue")
            image.save(temp_image, format="JPEG")
            temp_image.seek(0)

            payload = {"image": temp_image}
            res = self.client.patch(PROFILE_URL, payload, format="multipart")

            self.profile.refresh_from_db()
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertTrue(self.profile.image)

            image_path = self.profile.image.path
            self.assertTrue(os.path.exists(image_path))

            # Cleanup
            if os.path.exists(image_path):
                os.remove(image_path)
            self.assertFalse(os.path.exists(image_path))

    def test_delete_profile(self):
        """Test deleting the authenticated user's profile."""
        res = self.client.delete(PROFILE_URL)
        profile_exists = Profile.objects.filter(user=self.user).exists()
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(profile_exists)

    def test_like_a_profile(self):
        """Test liking a profile."""
        another_user = create_user(email="another@example.com")
        another_profile = Profile.objects.create(user=another_user, status="New user")

        url = LIKE_URL(another_profile.id)
        res = self.client.post(url)

        another_profile.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(another_profile.like_count, 1)

    def test_top_liked_profiles_hidden_without_payment(self):
        """Test that top liked profiles are not shown if the user has not paid."""
        another_user = create_user(email="likeduser@example.com")
        another_profile = Profile.objects.create(user=another_user, status="Popular")

        # Like the profile
        self.profile.liked_profiles.add(another_profile)

        res = self.client.get(TOP_LIKED_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 0)  # Expecting empty list since not paid

    def test_top_liked_profiles_shown_when_paid(self):
        """Test that top liked profiles are shown when the user has paid."""
        another_user = create_user(email="likeduser@example.com")
        another_profile = Profile.objects.create(user=another_user, status="Popular", like_count=10)

        # Like the profile
        self.profile.liked_profiles.add(another_profile)

        # Mark user as paid
        self.profile.is_paid = True
        self.profile.save()

        res = self.client.get(TOP_LIKED_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)  # Expecting 1 profile
        self.assertEqual(res.data[0]["id"], another_profile.id)  # Ensure correct profile is returned
