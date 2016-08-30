from rest_framework import viewsets
from rest_framework.filters import DjangoFilterBackend
from .models import *
from .serializers import *
from _base.backends import IsOwnerFilterBackend
from inkblob.viewsets import UploadModelViewSet

class ImageViewSet(UploadModelViewSet):

	#queryset = Image.objects.not_deleted()
	serializer_class = ImageSerializer
	filter_fields = ('content_type', 'object_id',)
	filter_backends = (IsOwnerFilterBackend, DjangoFilterBackend,)    