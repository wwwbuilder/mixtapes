from rest_framework import viewsets
from .models import *
from .serializers import *
from inkblob.viewsets import UploadModelViewSet

#http://www.django-rest-framework.org/api-guide/viewsets#modelviewset

class UserProfileViewSet(UploadModelViewSet):

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    
    def get_queryset(self):        
        profiles = UserProfile.objects.values('id', 'username')
        term = self.request.GET.get('q', None)
        if term:
            profiles = filter(lambda x: x['username'].lower().find(term) != -1, profiles)
        return profiles