from django.contrib.sites.models import get_current_site
from django.db import IntegrityError
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import DjangoFilterBackend

from .models import *
from .serializers import *
from inkblob.viewsets import UploadModelViewSet
from _base.backends import IsOwnerFilterBackend

#http://www.django-rest-framework.org/api-guide/viewsets#modelviewset

class MixtapeViewSet(UploadModelViewSet):

    #queryset = Mixtape.objects.not_deleted()
    serializer_class = MixtapeSerializer
    filter_backends = (IsOwnerFilterBackend, DjangoFilterBackend,)

    def create(self, request, *args, **kwargs):
        try:
            return super(MixtapeViewSet, self).create(request, *args, **kwargs)
        except IntegrityError:
            return HttpResponse(content='You already have a mixtape with the exact same title and artist.', status=500)
        except:
            return HttpResponse(content='Unexpected error. Please contact our support team.', status=500)

    @action()
    def send_approval_email(self, request, *args, **kwargs):
        try:
            mixtape_id = request.POST['mixtape_id']
            m = Mixtape.objects.get(id=mixtape_id)
            m.send_approval_email('http://%s' % (get_current_site(request)))
            return HttpResponse(content='Success', status=200)
        except:
            return HttpResponse(content='Error', status=500)

class TrackViewSet(UploadModelViewSet):

    #queryset = Track.objects.not_deleted()
    serializer_class = TrackSerializer
    filter_fields = ('mixtape',)
    filter_backends = (IsOwnerFilterBackend, DjangoFilterBackend,)
