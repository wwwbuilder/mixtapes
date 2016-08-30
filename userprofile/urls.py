from django.conf.urls import patterns, url
from django.views.generic import TemplateView

import views

urlpatterns = patterns('',
            url(r'^userprofileimage/$',views.UserProfileImageView.as_view(), name='userprofileimage'),
            url(r'^setprofileimage/$', views.SetProfileImageView.as_view(), name="setprofileimage"),
            
)