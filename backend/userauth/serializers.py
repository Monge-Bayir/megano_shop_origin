from rest_framework import serializers
from .models import Profile

class ProfileSerializers(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['fullName', 'email', 'phone', 'avatar']

    def get_image(self, obj):
        return obj.get_avatar()
