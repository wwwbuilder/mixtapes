from django.conf.urls import patterns, include, url
from django.views.generic import *
from .. import views

urlpatterns = patterns('',

    #url(r'^$', RedirectView.as_view(url=), name="base-my-account"),
    
    #url(r'^profile$', views.my_account.MyProfileView.as_view(), name="profile"),
    url(r'^my-profile/$', views.my_account.UserProfileUpdateView.as_view(), name='my_profile'),
    
    url(r'^my-mixtapes$', views.MyMixtapesView.as_view(), name="my_mixtapes"),
     url(r'^my-favorites$', views.FavoriteMixtapView.as_view(), name="my_favourites"),
    #url(r'^mixtape_detail/(?P<mixtapeid>[\d]*)$',views.my_account.MixtapeDetailView.as_view(), name='mixtape_detail'),
    url(r'^(?P<artist>[-\w]+)/(?P<slug>[-\w]+)/(?P<id>[-\w]+)/$', views.my_account.MixtapeDetailView.as_view(), name='mixtape_detail'),
    #url(r'^(?P<id>[-\w]+)/mixtapes/$', views.my_account.MixtapeDetailView.as_view(), name='mixtape_detail'),
    
    url(r'^addons$', views.MyAddonsView.as_view(), name="addons"),

    #Payments
    url(r'^payments$', views.PaymentsView.as_view(), name="payments"),
    url(r'^change-card$', views.ChangeCardView.as_view(), name="change-card"),
    url(r'^my-subscriptions/$', views.MySubscriptionsView.as_view(), name='my_subscriptions'),
    url(r'^my-membership/$', views.MyMembershipView.as_view(), name='my_subscriptions'),
    url(r'^premium-publisher/$', views.PremiumPublisherView.as_view(), name='premium-publisher'),
    url(r'^premium-member/$', views.PremiumMemberView.as_view(), name='premium-member'),
    url(r'^premium/$', views.PremiumView.as_view(), name='premium'),
    url(r'^subscribe_endpoint/$', views.SubscribeEndpointView.as_view(), name='subscribe_endpoint'),
    url(r'^upgrade-plan$', views.AJAXUpgradePlanView.as_view(), name="upgrade-plan"),
    url(r'^cancel-plan$', views.AJAXCancelPlanView.as_view(), name="cancel-plan"),
    url(r'^change-card$', views.TemplateView.as_view(template_name='my-payments.html'), name="change-card"),


    # url(r'^login$', TemplateView.as_view(template_name='login.html'), name="login"),
    # url(r'^my-connections$', TemplateView.as_view(template_name='my-connections.html'), name="my-connections"),
    # url(r'^my-account$', TemplateView.as_view(template_name='my-account.html'), name="my-account"),
    # url(r'^inactive$', TemplateView.as_view(template_name='inactive.html'), name="inactive"),
)