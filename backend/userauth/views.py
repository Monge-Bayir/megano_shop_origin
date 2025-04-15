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
from rest_framework import status

from .models import Profile

from rest_framework.views import APIView
from rest_framework.response import Response


class SignInView(APIView):
    def post(self, request):
        try:
            raw_data = list(request.data.keys())[0]
            data = json.loads(raw_data)
        except (IndexError, json.JSONDecodeError):
            return Response({'error': 'Invalid request format'}, status=400)

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return Response({'error': 'Username and password are required.'}, status=400)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return Response({'message': 'Login successful'}, status=200)
        else:
            return Response({'error': 'Invalid credentials'}, status=401)


class SignOutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)


class SignUpView(APIView):
    def post(self, request):
        try:
            raw_data = list(request.data.keys())[0]
            data = json.loads(raw_data)
            print(data)
            username = data.get('username')
            password = data.get('password')

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


        except Exception as e:
            return Response({'error': str(e)}, status=500)






