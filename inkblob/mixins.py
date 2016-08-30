from rest_framework import status
from rest_framework.response import Response

class SiteUploadMixin(object):

    def pre_save(self, obj):
        obj.created_by = self.request.user

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        self.pre_delete(obj)
        obj.deleted = True 
        obj.save()
        self.post_delete(obj)
        return Response(status=status.HTTP_204_NO_CONTENT)