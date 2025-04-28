from django.db import models
from django.contrib.auth.models import User


def upload_avatar_path(instance: 'Profile', filename: str) -> str:
    return f'profiles/profile_{instance.pk}/avatar/{filename}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    fullName = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    phone = models.CharField(max_length=12)
    email = models.EmailField(default='example@mail.ru')
    surname = models.CharField(max_length=100)
    avatar = models.ImageField(
        null=True,
        blank=True,
        upload_to=upload_avatar_path
    )

    def __str__(self):
        return self.fullName

    def get_avatar(self):
        avatar = {
            'src': self.avatar.url,
            'alt': self.avatar.name
        }
        return avatar