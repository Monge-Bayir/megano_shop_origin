from django.urls import path

from .models import Profile
from .views import SignUpView, SignOutView, SignInView, ProfileApiView

app_name = 'userauth'

urlpatterns = [
    path('sign-in', SignInView.as_view(), name='sign-in'),
    path('sign-up', SignUpView.as_view(), name='sign-up'),
    path('sign-out', SignOutView.as_view(), name='sign-out'),
    path('profile', ProfileApiView.as_view())
]