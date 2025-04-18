import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers import serialize
from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import UpdateView, DetailView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Profile

from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import (
    ProfileDetailSerializer,
    ProfileUpdateSerializer,
    EmailUpdateSerializer,
    AvatarUploadSerializer, ChangePasswordSerializer
)



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


# class ProfileApiView(APIView):
#     def get(self, request):
#         profile = get_object_or_404(Profile, user=request.user)
#         serializer = ProfileSerializers(profile)
#         return Response(serializer.data)
#
#     def post(self, request):
#         serializer = ProfileSerializers(data=request.data)
#         if serializer.is_valid():
#             return Response(serializer.data, status=201)
#         return Response(status=400)


from rest_framework.parsers import MultiPartParser, FormParser

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Profile
from .serializers import ProfileUpdateSerializer

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Profile
from .serializers import ProfileUpdateSerializer

class ProfileDetailAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]  # Для работы с файлами

    def get(self, request):
        # Получаем профиль пользователя
        profile = request.user.profile  # Пример: связь с профилем текущего пользователя
        serializer = ProfileUpdateSerializer(profile)
        return Response(serializer.data)

    def post(self, request):
        # Получаем текущий профиль пользователя
        profile = request.user.profile  # Пример: связь с профилем текущего пользователя

        # Создаем сериализатор для обновления
        serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()  # Сохраняем изменения
            return Response({"detail": "Профиль успешно обновлён"}, status=200)

        # В случае ошибки, возвращаем ошибки
        return Response(serializer.errors, status=400)



class AvatarUploadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = request.user.profile
        serializer = AvatarUploadSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Аватар успешно обновлён'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import ChangePasswordSerializer  # Подключаем наш сериализатор


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        current_password = serializer.validated_data['currentPassword']

        if not user.check_password(current_password):
            return Response({'detail': 'Неверный текущий пароль'}, status=status.HTTP_400_BAD_REQUEST)

        new_password = serializer.validated_data['newPassword']
        user.set_password(new_password)
        user.save()

        return Response({'detail': 'Пароль изменён'}, status=status.HTTP_200_OK)







