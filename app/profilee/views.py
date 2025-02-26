from rest_framework import generics, status
from rest_framework.response import Response
from core.models import Profile
from .serializers import ProfileSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    """Allow users to retrieve, update, or delete their profile, ensuring only one profile per user."""
    serializer_class = ProfileSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Retrieve the authenticated user's profile."""
        return Profile.objects.get(user=self.request.user)


class ProfileCreateView(generics.CreateAPIView):
    """Allow authenticated users to create a profile only if they don't have one."""
    serializer_class = ProfileSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Ensure a user can create only one profile."""
        if Profile.objects.filter(user=request.user).exists():
            return Response(
                {"detail": "You already have a profile."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().create(request, *args, **kwargs)

class LikeProfileView(generics.GenericAPIView):
    """Allow users to like a profile."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        profile = Profile.objects.get(pk=kwargs['pk'])
        profile.like()
        return Response({"message": "Profile liked!"}, status=status.HTTP_200_OK)

class TopLikedProfilesView(generics.ListAPIView):
    """Show top 5 profiles that the authenticated user has liked, if they have paid."""
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_profile = Profile.objects.get(user=self.request.user)
        if user_profile.is_paid:
            return Profile.objects.filter(liked_by=user_profile).order_by('-like_count')[:5]
        return Profile.objects.none()  # Return an empty queryset if not paid
