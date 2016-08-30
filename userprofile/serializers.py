from .models import *
from _base.serializers import *
from _misc.models import Image
from userprofile.models import UserProfile
from rest_framework import serializers

class UserProfileSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('username', 'id')
        
        
        
class UserProfileImageSerializer(serializers.ModelSerializer):
        cdn_url = serializers.Field(source='cdn_url')
        small_profile_image = serializers.Field(source='get_thumbnail')

        class Meta:
                model = Image

