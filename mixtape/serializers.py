from .models import *
from _base.serializers import *
from _base.backends import IsOwnerFilterBackend
from rest_framework import serializers
from userprofile.serializers import UserProfileSerializer
from _misc.models import Image
from userprofile.models import UserProfile

class MixtapeSerializer(DynamicFieldsModelSerializer):
    full_mixtape_slug = serializers.Field(source='full_mixtape_slug')
    content_type_id = serializers.Field(source='get_content_type_id')    

    class Meta:
        model = Mixtape

class TrackSerializer(DynamicFieldsModelSerializer):
    # artists = UserProfileSerializer(many=True)
    # producers = UserProfileSerializer(many=True)
    # djs = UserProfileSerializer(many=True)

    prepopulate_artists = serializers.SerializerMethodField('get_prepopulate_artists')
    prepopulate_producers = serializers.SerializerMethodField('get_prepopulate_producers')
    prepopulate_djs = serializers.SerializerMethodField('get_prepopulate_djs')

    def get_prepopulate_artists(self, obj):
        return obj.artists.values('id', 'username')

    def get_prepopulate_producers(self, obj):
        return obj.producers.values('id', 'username')

    def get_prepopulate_djs(self, obj):
        return obj.djs.values('id', 'username')                

    class Meta:
        model = Track
    
class MixtapeImageSerializer(serializers.ModelSerializer):
        cdn_url = serializers.Field(source='cdn_url')
        small_profile_image = serializers.Field(source='get_thumbnail')
       
        class Meta:
                model = Image
                
class GenreNestedSerializer(serializers.ModelSerializer):
        class Meta:
                model = Genre
                fields = ('name', 'id',)
                
class UserProfileNestedSerializer(serializers.ModelSerializer):
        class Meta:
                model = UserProfile
                fields = ('username', 'id',)

        
class TrackSerializer(serializers.ModelSerializer):
        mixtape = serializers.PrimaryKeyRelatedField()
        genres = GenreNestedSerializer(many=True)
        artists = UserProfileNestedSerializer(many=True)
        producers = UserProfileNestedSerializer(many=True)
        djs = UserProfileNestedSerializer(many=True)
        #other_genres = serializers.Field(source='other_genres')

        class Meta:
                model = Track

class MixtapeTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        

class MixtapeAddonSerializer(serializers.ModelSerializer):
        class Meta:
                model = AddonType

