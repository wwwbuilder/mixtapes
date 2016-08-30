from inkblob.mixins import SiteUploadMixin
from rest_framework import viewsets

class UploadModelViewSet(SiteUploadMixin, viewsets.ModelViewSet):
    pass