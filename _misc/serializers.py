from _base.serializers import *
from .models import *
from rest_framework import serializers

class ImageSerializer(DynamicFieldsModelSerializer):
    thumbnail = serializers.Field(source='get_thumbnail')

    class Meta:
        model = Image