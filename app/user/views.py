"""
Views for the user API.
"""

from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)


class CreateUserView(generics.CreateAPIView):
    """
    Create a new user in the system.

    - This view handles user registration.
    - It uses `CreateAPIView`, which provides a default implementation
      for handling HTTP POST requests to create new objects.
    - The `UserSerializer` is used to validate and create the user.
    """

    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """
    Create a new authentication token for the user.

    - This view allows users to obtain a token by providing valid credentials.
    - It extends `ObtainAuthToken`, which is a built-in DRF view that
      validates user credentials and returns an authentication token.
    - Uses `AuthTokenSerializer` for authentication.
    - Uses `renderer_classes` to support rendering responses in different formats
      (e.g., JSON, Browsable API).
    """

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """
    Manage the authenticated user.

    - Allows the user to retrieve or update their own profile.
    - `RetrieveUpdateAPIView` is used since it supports both `GET` (to retrieve user details)
      and `PATCH/PUT` (to update user details).
    - Uses `TokenAuthentication` to ensure that only authenticated users
      can access this endpoint.
    - `permissions.IsAuthenticated` ensures that anonymous users cannot
      access or modify the data.
    """

    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Retrieve and return the authenticated user.

        - Instead of querying for a user manually, `self.request.user`
          provides the authenticated user based on the token provided.
        - This ensures that users can only access their own profile and not others.
        """
        return self.request.user
