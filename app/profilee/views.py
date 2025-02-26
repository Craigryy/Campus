from rest_framework import generics
from core.models import Profile
from .serializers import ProfileSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    """Allow users to retrieve, update, or delete their profile."""
    serializer_class = ProfileSerializer

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user's profile, creating one if needed."""
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile
