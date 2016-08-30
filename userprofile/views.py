import ujson as json
from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404, HttpResponse, HttpResponseBadRequest
from django.views.generic import ListView, View
from _misc.models import Image
from userprofile.serializers import UserProfileImageSerializer

from braces.views import (
	JSONResponseMixin, AjaxResponseMixin
	)

from Mixtapes.utils.access import LoginRequiredMixin

class UserProfileLookupView(LoginRequiredMixin, JSONResponseMixin, AjaxResponseMixin, ListView):

	def get_queryset(self):
		pass
	

from rest_framework import viewsets
from rest_framework.decorators import link, action
# action = POST, link = GET

class PreSaveMixin(object):
		def pre_save(self, obj):
				obj.slug = slugify(obj.name)
				obj.created_by = self.request.user
								
								
class UserProfileImageViewSet(viewsets.ModelViewSet):
        queryset = Image.objects.order_by('-updated')
        serializer_class = UserProfileImageSerializer
        filter_fields = ('userprofile',)
		
		
class UserProfileImageView(JSONResponseMixin, AjaxResponseMixin, View):
		
	def post_ajax(self, request, *args, **kwargs):
		
		responsedict = {}
		data = self.request._post
		print data
		try:
				userprofile_obj = request.user.userprofile
				image_obj = Image(url=data['url'], filename=data['filename'],mimetype=data['mimetype'],
								  size=data['size'],key=data['awskey'],object_id=data['object_id'],
								  content_type_id=userprofile_obj.get_content_type_id(),created_by=request.user,
								  updated_by=request.user) 
				image_obj.save()
				responsedict['success'] = True

		except:
				responsedict['success'] = False

		return HttpResponse(json.dumps(responsedict), mimetype="application/json")
		
class SetProfileImageView(LoginRequiredMixin, AjaxResponseMixin, JSONResponseMixin, View):
		def post_ajax(self, request, *args, **kwargs):
				responsedict = {}
				data = json.loads(self.request.body)
				defaultpk = data['defaultimage']

				try:
						image_obj = Image.objects.get(pk=defaultpk)
						image_obj.save()
						responsedict['success'] = True

				except:
						responsedict['success'] = False

				return HttpResponse(json.dumps(responsedict), mimetype="application/json")

