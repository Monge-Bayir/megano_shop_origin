from django.urls import path

from .models import Profile
from .views import sign_in_view, sign_up_view, sign_out_view, ProfileUpdate, ProfileDetailView, change_password

app_name = 'api'

urlpatterns = [
    path('sign-in', sign_in_view, name='sign-in'),
    path('sign-up', sign_up_view, name='sign-up'),
    path('sign-out', sign_out_view, name='sign-out'),
    path('profile', ProfileUpdate.as_view(), name='profile-update'),
    path('profile', change_password, name='password')
    # path('profile/avatar', ProfileDetailView, name='profile-detail'),
]