from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.views.generic import TemplateView
from mixtape.views import limit_download, MixtapeUploadView, AutocompleteUserProfileViewSet, MixtapeCreateView, captcha_download, TestView, PhoneVerifyView, PhoneReVerifyView, MyEmailView, \
     MixtapeImageView, TrackListView, NotifyAdminView, MixtapeImageViewSet, TrackViewSet, HomeView, \
     MixtapesListView, UserProfileListView, DownloadView, UserProfileDetailView, AddonsDetailView,\
    AddonsCheckoutView, MixtapeAddonViewSet, AboutUsView, FeaturedMixtapView, RecentMixtapView,download_sampleTrack, \
    HotThisWeekMixtapView, TwilioVerificationView, SignupView,AddArtistView, AddUserProfileView, UserAcknowledgementView,\
    RapMixtapView, BlendsMixtapView, ReggaeMixtapView, EastCoastMixtapView, DirtySouthMixtapView, RBMixtapView, ChoppedMixtapView, InstrumentalsMixtapView,\
    validateSignupForm, ContactUsView, AutocompleteTrackViewSet,SearchView,AnalyticsTrackView,TermsView,PrivacyView,DMCAView,AdvertiseView,AddContactUsView,AddFavorite,AddSubscriptionView,TrackView,SignedUrlView,\
    UpcomingMixtapView,TopOfMonthMixtapView, AddStreamCount,fp_details
from userprofile.views import UserProfileImageViewSet

admin.autodiscover()

#Declare the django rest-framework router
from rest_framework.routers import DefaultRouter
from . import viewsets

router = DefaultRouter()
router.register(r'mixtapes', viewsets.MixtapeViewSet,base_name='mixtapes')
router.register(r'tracks', viewsets.TrackViewSet, base_name= 'tracks')
router.register(r'userprofiles', viewsets.UserProfileViewSet, base_name= 'userprofiles')
router.register(r'mixtapeimage-viewset', MixtapeImageViewSet, base_name= 'images')
router.register(r'track-viewset',TrackViewSet, base_name= 'tracks')
router.register(r'autocompleteuserprofile-viewset', AutocompleteUserProfileViewSet)
router.register(r'autocompletetrack-viewset', AutocompleteTrackViewSet)

router.register(r'userprofileimage-viewset', UserProfileImageViewSet)
router.register(r'mixtapeaddon-viewset', MixtapeAddonViewSet)



urlpatterns = patterns('',

    #Django rest-framework
    url(r'^routers/', include(router.urls)),
    url(r'^email/$', MyEmailView.as_view(), name="account_email"),
    url(r'', include('allauth.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r"^ratings/", include("agon_ratings.urls")),
    url(r"^likes/", include("phileo.urls")),
    url(r'^adminmt/', include(admin.site.urls)),    
    url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    
    #url(r'^payments/', include('payments.urls')),
    #The default views (i.e. change card are not needed here)

    url('', include('social.apps.django_app.urls', namespace='social')),  

    #url(r'^$', TemplateView.as_view(template_name='home.html'), name="home"),
    url(r'^$', HomeView.as_view(), name="home"),
    #url(r'^login$', TemplateView.as_view(template_name='login.html'), name="login"),

    url(r'^my-connections$', TemplateView.as_view(template_name='my-connections.html'), name="my-connections"),
    
    url(r'', include('Mixtapes.other_urls.my_account_urls', namespace='my-account')),
    url(r'', include('userprofile.urls', namespace='userprofile')),    
    
    
    #url(r'^upload/$', MixtapeUploadView.as_view(), name='upload'),    
    url(r'^upload/(?P<mixtapeid>[\d]*)$', MixtapeUploadView.as_view(), name="mixtape_create"),
    url(r'^mixtape_list/(?P<mixtapeid>[\d]*)$',MixtapeCreateView.as_view(), name='mixtape-list'),
    url(r'^image-list/(?P<object_id>[\d]*)$',MixtapeImageView.as_view(),name='image-list'),
    url(r'^track-list/(?P<object_id>[\d]*)$',TrackListView.as_view(),name='track-list'),
    url(r'^notifyadmin/$', NotifyAdminView.as_view(), name='notify_admin'),

    url(r'^inactive$', TemplateView.as_view(template_name='inactive.html'), name="inactive"),

    #url(r'^mixtapes/', include('mixtape.urls', namespace='mixtape')),
    url(r'^mixtapes/$', MixtapesListView.as_view(), name='all_mixtape_list'),
    url(r'^people/$', UserProfileListView.as_view(), name='artists'),
    url(r'^download/(?P<mixtapeid>[\d]*)$',DownloadView.as_view(), name='download'),

    url(r'^user/(?P<slug>[-\w+]*)/$', UserProfileDetailView.as_view(), name='user'),
    url(r'^(?P<id>[-\w]+)/addons/$', AddonsDetailView.as_view(), name='addons_detail'),
    url(r'^addons-checkout/$', AddonsCheckoutView.as_view(), name='addons_checkout'),
    url(r'^about-us/$', AboutUsView.as_view(), name='aboutus'),
    url(r'^addfavorite/$', AddFavorite.as_view(), name='addfavorite'),
    url(r'^addstreamcount/$', AddStreamCount.as_view(), name='addstreamcount'),
    url(r'^track/$', TrackView.as_view(), name='track'),
    url(r'^signedtrack/$', SignedUrlView.as_view(), name='signedtrack'),
    url(r'^terms/$', TermsView.as_view(), name='terms'),
    url(r'^privacy/$', PrivacyView.as_view(), name='privacy'),
    url(r'^dmca/$', DMCAView.as_view(), name='dmca'),
    url(r'^advertise/$', AdvertiseView.as_view(), name='advertise'),
    url(r'^featured-mixtapes/$',FeaturedMixtapView.as_view(), name='featured_mixtapes'),
    url(r'^upcoming-mixtapes/$',UpcomingMixtapView.as_view(), name='upcoming_mixtapes'),
    url(r'^recent-mixtapes/$',RecentMixtapView.as_view(), name='recent_mixtapes'),
    url(r'^hot-this-week/$',HotThisWeekMixtapView.as_view(), name='hot_this_week'),
    url(r'^top-of-month/$',TopOfMonthMixtapView.as_view(), name='hot_this_week'),
    url(r'^twilio_verification/$',TwilioVerificationView.as_view(),name='twilio_verification'),
    url(r'^registration/$',SignupView.as_view(), name='registration'),
    url(r'^adduserprofile/$',AddUserProfileView.as_view(), name='adduserprofile'),
    url(r'^addartist/$',AddArtistView.as_view(), name='addartist'),
    url(r'^addcontactus/$',AddContactUsView.as_view(), name='addcontactus'),
    url(r'^addsubcribe/$',AddSubscriptionView.as_view(), name='addsubcribe'),
    url(r'^acknowldgement/$',UserAcknowledgementView.as_view(), name='acknowledgment'),
    url(r'^validate_form/$', validateSignupForm.as_view(), name='validate_form'),
    url(r'^contactus/$', ContactUsView.as_view(), name="contactus"),
    url(r'^limitdownload/$', limit_download, name="limit_download"),
    url(r'^search/$', SearchView.as_view(), name="contactus"),
    url(r'^addtrackingcode/$', AnalyticsTrackView.as_view(), name="Analytics_Track"),
    url(r'^downloadsample/(\w*)$', download_sampleTrack, name="download_sample"),
    url(r'^fpdetails/$', fp_details, name="fp_details"),
    

    #for captcha
    url(r'^test_dwnld/$', captcha_download, name="test_dwnld"),
    
    url(r'^phone-verify/$', TestView.as_view(), name="ph_verify"),
    url(r'^verify/$', PhoneVerifyView.as_view(), name="verify"),
    url(r'^reverify/$', PhoneReVerifyView.as_view(), name="reverify"),

    # urls added for Genre
    url(r'^rap-mixtapes/$',RapMixtapView.as_view(), name='rap_mixtapes'),
    url(r'^blends-mixtapes/$',BlendsMixtapView.as_view(), name='blend_mixtapes'),
    url(r'^reggae-mixtapes/$',ReggaeMixtapView.as_view(), name='reggae_mixtapes'),
    url(r'^east-coast-mixtapes/$',EastCoastMixtapView.as_view(), name='eastcoast_mixtapes'),
    url(r'^dirty-south-mixtapes/$',DirtySouthMixtapView.as_view(), name='dirtysouth_mixtapes'),
    url(r'^rnb-mixtapes/$',RBMixtapView.as_view(), name='rnb_mixtapes'),
    url(r'^chopped-screwed-mixtapes/$',ChoppedMixtapView.as_view(), name='chopped_mixtapes'),
    url(r'^instrumentals-mixtapes/$',InstrumentalsMixtapView.as_view(), name='instrumentals_mixtapes'),



)

from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    
if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))

