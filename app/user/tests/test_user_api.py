"""
Tests for the user API.
"""
from django.test import TestCase  # Base test case class for Django tests
from django.contrib.auth import get_user_model  # Function to get the user model dynamically
from django.urls import reverse  # Helper to generate URLs dynamically

from rest_framework.test import APIClient  # Test client for making API requests
from rest_framework import status  # Module for HTTP response status codes

# Define endpoint URLs using Django's reverse() function
CREATE_USER_URL = reverse('user:create')  # URL for creating a new user
TOKEN_URL = reverse('user:token')  # URL for obtaining authentication token
ME_URL = reverse('user:me')  # URL for retrieving/updating the authenticated user


def create_user(**params):
    """Helper function to create a user in the database."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test public (unauthenticated) user API features."""

    def setUp(self):
        """Initialize the test client before each test."""
        self.client = APIClient()

    def test_create_user_success(self):
        """Test that creating a user is successful."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)  # Send a POST request to create a user

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)  # Expect a 201 response
        user = get_user_model().objects.get(email=payload['email'])  # Retrieve the user from the database
        self.assertTrue(user.check_password(payload['password']))  # Ensure the password is stored securely
        self.assertNotIn('password', res.data)  # Ensure the password is not returned in the response

    def test_user_with_email_exists_error(self):
        """Test that an error is returned if the user already exists."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        create_user(**payload)  # Create a user first
        res = self.client.post(CREATE_USER_URL, payload)  # Try creating the same user again

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  # Expect a 400 error

    def test_password_too_short_error(self):
        """Test that an error is returned if the password is too short."""
        payload = {
            'email': 'test@example.com',
            'password': 'pw',  # Too short
            'name': 'Test name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  # Expect a 400 error
        user_exists = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exists)  # Ensure the user is not created

    def test_create_token_for_user(self):
        """Test that a token is generated for valid user credentials."""
        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'test-user-password123',
        }
        create_user(**user_details)  # Create a user

        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }  # Token request only requires email and password
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)  # Ensure token is in response
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # Expect a 200 success response

    def test_create_token_bad_credentials(self):
        """Test that an error is returned if credentials are invalid."""
        create_user(email='test@example.com', password='goodpass')
        payload = {'email': 'test@example.com', 'password': 'badpass'}  # Incorrect password
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)  # Ensure no token is returned
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  # Expect a 400 error

    def test_create_token_email_not_found(self):
        """Test that an error is returned if the email is not registered."""
        payload = {'email': 'test@example.com', 'password': 'pass123'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)  # Ensure no token is returned
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  # Expect a 400 error

    def test_create_token_blank_password(self):
        """Test that an error is returned if the password is blank."""
        payload = {'email': 'test@example.com', 'password': ''}  # Empty password
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required to access user details."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)  # Expect a 401 error


class PrivateUserApiTests(TestCase):
    """Test API endpoints that require authentication."""

    def setUp(self):
        """Create a user and authenticate requests before each test."""
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)  # Authenticate the test client

    def test_retrieve_profile_success(self):
        """Test retrieving profile for authenticated user."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })  # Ensure the response contains the correct user data

    def test_post_me_not_allowed(self):
        """Test that POST requests are not allowed for the profile endpoint."""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)  # Expect a 405 error

    def test_update_user_profile(self):
        """Test updating the authenticated user's profile."""
        payload = {'name': 'Updated name', 'password': 'newpassword123'}
        res = self.client.patch(ME_URL, payload)  # Partial update

        self.user.refresh_from_db()  # Reload user from the database
        self.assertEqual(self.user.name, payload['name'])  # Ensure name is updated
        self.assertTrue(self.user.check_password(payload['password']))  # Ensure password is updated securely
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # Expect a 200 success response
