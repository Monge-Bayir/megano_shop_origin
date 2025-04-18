from rest_framework import serializers
from .models import Profile
from django.contrib.auth.models import User

class ProfileDetailSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['fullName', 'email', 'phone', 'avatar']

    def get_avatar(self, obj):
        if obj.avatar:
            return {
                "src": obj.avatar.url,
                "alt": obj.avatar.name
            }
        return {
            "src": "/static/img/no-avatar.png",  # заглушка
            "alt": "No avatar"
        }

from rest_framework import serializers
from .models import Profile

from rest_framework import serializers
from .models import Profile

class ProfileUpdateSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False)  # Это изображение, и оно может быть необязательным

    class Meta:
        model = Profile
        fields = ['fullName', 'phone', 'email', 'avatar']  # Добавляем все поля профиля


class EmailUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']


class AvatarUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['avatar']


class ChangePasswordSerializer(serializers.Serializer):
    currentPassword = serializers.CharField(write_only=True)
    newPassword = serializers.CharField(write_only=True)

    def validate(self, attrs):
        new_password = attrs.get('newPassword')

        if len(new_password) < 6:
            raise serializers.ValidationError("Пароль должен быть не менее 6 символов")

        return attrs
