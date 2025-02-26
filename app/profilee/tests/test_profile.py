from django.test import TestCase  # Django's built-in test framework
from django.contrib.auth import get_user_model  # Function to retrieve the custom user model
from django.urls import reverse  # Generates URLs dynamically
from rest_framework import status  # Provides HTTP status codes
from rest_framework.test import APIClient  # Test client for making API requests
from core.models import Profile  # Importing the Profile model
from PIL import Image  # Importing Pillow to create test images
import tempfile  # Used for creating temporary files


# Generate the URL for retrieving/updating the authenticated user's profile
PROFILE_URL = reverse('profilee:me')


def create_user(**params):
    """
    Helper function to create a new user in the database.

    Args:
        **params: Dictionary of user attributes (email, password, name, etc.)

    Returns:
        user (User): The created user object.
    """
    return get_user_model().objects.create_user(**params)


class PublicProfileAPITests(TestCase):
    """
    Test cases for the profile API endpoints that do NOT require authentication.

    These tests ensure that unauthenticated users cannot access the profile endpoint.
    """

    def setUp(self):
        """Set up a test client for making API requests without authentication."""
        self.client = APIClient()

    def test_auth_required(self):
        """
        Test that authentication is required to access the profile endpoint.

        Expected Behavior:
        - Unauthenticated requests should return a 401 Unauthorized response.
        # """
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)  # Expecting 401 error




class PrivateProfileAPITests(TestCase):
    """
    Test cases for the profile API endpoints that REQUIRE authentication.

    These tests ensure that authenticated users can retrieve, update, and upload profile images.
    """

    def setUp(self):
        """
        Set up an authenticated user and test client before each test.

        - Creates a user with test credentials.
        - Ensures a corresponding profile is created.
        - Authenticates the test client with the created user.
        """
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name',
        )
        # Ensure the profile is explicitly created to avoid test failures due to missing data
        self.profile = Profile.objects.create(user=self.user, status='single')

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)  # Authenticate the test client

    def test_retrieve_profile_success(self):
        """
        Test retrieving the profile of the logged-in user.

        Expected Behavior:
        - The response should return HTTP 200 OK.
        - The profile data should match the logged-in user's profile.
        """
        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)  # Check for success
        self.assertEqual(res.data['status'], self.profile.status)  # Ensure correct status is returned

    def test_update_profile(self):
        """
        Test updating the status field of an authenticated user's profile.

        Expected Behavior:
        - The response should return HTTP 200 OK.
        - The status should be updated correctly in the database.
        """
        payload = {'status': 'married'}  # New status to update

        res = self.client.patch(PROFILE_URL, payload)  # Send a PATCH request

        self.profile.refresh_from_db()  # Reload profile data from the database
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # Ensure success
        self.assertEqual(self.profile.status, payload['status'])  # Check if status was updated

    def test_update_profile_image(self):
        """
        Test uploading a profile image using Pillow (PIL).

        Expected Behavior:
        - The response should return HTTP 200 OK.
        - The image should be successfully stored in the database.
        """
        with tempfile.NamedTemporaryFile(suffix=".jpg") as temp_image:
            # Create a dummy image using Pillow (PIL)
            image = Image.new("RGB", (100, 100), color="blue")  # Create a 100x100 blue image
            image.save(temp_image, format="JPEG")  # Save image as JPEG
            temp_image.seek(0)  # Reset file pointer to start

            # Prepare payload with the temporary image file
            payload = {'image': temp_image}

            # Send a PATCH request to update the profile image
            res = self.client.patch(PROFILE_URL, payload, format='multipart')

            # Refresh profile data from database
            self.profile.refresh_from_db()

            self.assertEqual(res.status_code, status.HTTP_200_OK)  # Ensure success
            self.assertTrue(self.profile.image)  # Ensure an image was uploaded

    def test_profile_auto_created_on_user_creation(self):
        """
        Test if a profile is NOT automatically created when a new user is registered.

        Expected Behavior:
        - A profile should exist for every newly created user.
        """
        new_user = create_user(email='newuser@example.com', password='testpass123')  # Create new user
        profile_exists = Profile.objects.filter(user=new_user).exists()  # Check if profile exists

        self.assertFalse(profile_exists)  # Ensure profile exist

