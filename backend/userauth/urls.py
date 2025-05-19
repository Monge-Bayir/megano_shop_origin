from django.urls import path

from .models import Profile
from .views import SignUpView, SignOutView, SignInView, ProfileDetailAPIView, ChangePasswordAPIView, AvatarUploadAPIView

app_name = 'userauth'

urlpatterns = [
    path('sign-in/', SignInView.as_view(), name='sign-in'),
    path('sign-up/', SignUpView.as_view(), name='sign-up'),
    path('sign-out/', SignOutView.as_view(), name='sign-out'),
    path('profile/', ProfileDetailAPIView.as_view(), name='profile'),
    path('profile/password/', ChangePasswordAPIView.as_view(), name='change-password'),
    path('profile/avatar/', AvatarUploadAPIView.as_view(), name='upload-avatar')
]