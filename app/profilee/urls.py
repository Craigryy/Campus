from django.urls import path
from profilee import views

app_name = 'profilee'

urlpatterns = [
    path('me/', views.ProfileView.as_view(), name='me'),
]

