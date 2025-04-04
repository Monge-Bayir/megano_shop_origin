import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import UpdateView, DetailView

from .models import Profile


def sign_in_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        body = json.loads(request.body)
        username = body['username']
        password = body['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=500)


def sign_out_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return HttpResponse(status=200)


def sign_up_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        body = json.loads(request.body)
        username = body['username']
        password = body['password']

        user = User.objects.create_user(
            username=username,
            password=password
        )
        user.save()

        Profile.objects.create(username=username)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=500)


class ProfileUpdate(LoginRequiredMixin, UpdateView):
    model = Profile
    fields = ['avatar', 'fullName', 'phone', 'email']
    template_name = 'frontend/profile.html'

    def get_object(self, queryset=None):
        return self.request.user


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'frontend/profile.html'

    def get_object(self, queryset=None):
        return self.request.user


# def password_change_password(request: HttpRequest) -> HttpResponse:
#     if request.method == 'POST':
#         body = json.loads(request.body)
#
@login_required
def change_password(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

    try:
        data = json.loads(request.body)
        current_password = data.get('passwordCurrent')
        new_password = data.get('password')
        confirm_password = data.get('passwordReply')
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user = request.user

    if not current_password or not new_password or not confirm_password:
        return JsonResponse({'error': 'All fields are required'}, status=400)

    if not user.check_password(current_password):
        return JsonResponse({'error': 'Incorrect current password'}, status=400)

    if new_password != confirm_password:
        return JsonResponse({'error': 'New passwords do not match'}, status=400)

    if len(new_password) < 8:
        return JsonResponse({'error': 'New password must be at least 8 characters'}, status=400)

    user.set_password(new_password)
    user.save()
    update_session_auth_hash(request, user)

    return JsonResponse({'success': 'Password changed successfully'})