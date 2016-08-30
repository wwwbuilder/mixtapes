from rest_framework import serializers
from mixtape.models import (
        Mixtape, Track
)
from userprofile.models import UserProfile

base_object_fields = (
        'slug', 'name', 'updated', 'created',
        'youtube_video', 'featured', 'promoted',
        'sponsor', 'created_by')


class MixtapeSerializer(serializers.ModelSerializer):
        primaryArtist_slug = serializers.Field(source='primaryArtist_slug')
        primaryGenre = serializers.PrimaryKeyRelatedField()
        created_by = serializers.PrimaryKeyRelatedField(required=False)
        amazon_url = serializers.Field(source='amazon_url')
        fullAlbumName = serializers.Field(source='fullAlbumName')

        class Meta:
                model = Mixtape
                
                
class UserProfileSerializer(serializers.ModelSerializer):
        text = serializers.Field(source='username')
        id = serializers.Field('id')

        class Meta:
                model = UserProfile
                fields = ('text', 'id',)



