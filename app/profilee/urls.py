from django.urls import path
from profilee import views

app_name = 'profilee'

urlpatterns = [
    # Retrieve, update, delete profile
    path('me/', views.ProfileView.as_view(), name='me'),
    path(
        'create/',
        views.ProfileCreateView.as_view(),
        name='create'),

    path('<int:pk>/like/', views.LikeProfileView.as_view(), name='like-profile'),
    path('top-liked/', views.TopLikedProfilesView.as_view(), name='top-liked-profiles'),
]
