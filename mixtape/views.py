import re
import pytz
import random 
from datetime import timedelta,datetime
from django.utils import timezone
import ujson as json
from StringIO import StringIO  
from zipfile import ZipFile  
from random import randint
import shutil
from django.conf import settings
from django.utils import timezone
import os.path
from braces.views import JSONResponseMixin, AjaxResponseMixin, CsrfExemptMixin
from Mixtapes.utils.access import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from operator import itemgetter

from django.contrib import messages

from django.contrib.auth import authenticate, login
from django.core.cache import cache
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.views.generic import *
from django.db.models import Q
from django.contrib.auth.hashers import make_password

from twilio.rest import TwilioRestClient

from allauth.socialaccount import views as signup_views
from allauth.account import signals
from allauth.account.utils import complete_signup
from allauth.account import app_settings
from allauth.account.views import EmailView


from userprofile.models import UserProfile,ArtistSubscription
from .models import Mixtape, Genre, Track, AddonType, AddonCharge, MixtapePageView, MixtapeSpotLight,AddonCategory, MixtapeDownloadLimit,MixtapeFavorite
from mixtape.serializers import MixtapeSerializer, MixtapeAddonSerializer, UserProfileSerializer, MixtapeImageSerializer, TrackSerializer ,MixtapeTrackSerializer

from Mixtapes.forms import MixtapeCreateForm, UserProfileCreateForm
from _misc.models import Image
from .tasks import *
from .view_mixins import PaymentRequiredMixin
from verify.models import TwilioVerification
from mixtape.forms import SignupForm

from recaptcha.client import captcha  

from rest_framework import viewsets
from rest_framework.decorators import link, action
class PreSaveMixin(object):
        def pre_save(self, obj):
                obj.slug = slugify(obj.name)
                obj.created_by = self.request.user


class AddonsDetailView(LoginRequiredMixin, PaymentRequiredMixin, DetailView):
        template_name = 'mixtape/addons_detail.html'
        model = Mixtape

        def get_object(self):
                try:
                    mt = Mixtape.objects.get(id=self.kwargs['id'])
                    if mt.created_by.id == self.request.user.pk:
                        return mt
                except:
                    mt = ''

        def get_context_data(self, **kwargs):
                context = super(AddonsDetailView, self).get_context_data(**kwargs)
                mt = context['object']
                if mt != None:
                    active = mt.active_addons
                    all_addons = AddonType.objects.all()
                    cats = AddonCategory.objects.all()
                    if active:
                            for a in active:
                                    other = all_addons.exclude(id=a.id)
                    other = all_addons

                    other_categories = [{'name':c.name,'id':c.id, 'addons':filter(lambda x: x.category == c, other)} for c in cats]


                    context['active'] = active
                    context['other'] = other_categories
                else:
                    messages.warning(self.request, 'Mixtape of other users can not be edited')
                return context


class AddonsCheckoutView(LoginRequiredMixin, AjaxResponseMixin, JSONResponseMixin, View):
        def post_ajax(self, request, *args, **kwargs):
                data = json.loads(self.request.body)
                addonids = data['addons']
                mixtape = data['mixtape']
                responsedict = {}
                mo = Mixtape.objects.get(pk=mixtape)
                print '\n%s\n' % mo.name

                try:
                        for aid in addonids:
                                ao = AddonType.objects.get(id=int(aid))
                                ac = AddonCharge.create_charge(userobj=self.request.user, addonobj=ao, mixtapeobj=mo)
                                print '%s - SUCCESS!' % ao.name
                        messages.success(request, 'Addons created!')
                        responsedict['success'] = True
                except Exception,e:
                        print e
                        messages.info(request, 'Addons created!')
                        responsedict['success'] = False

                return HttpResponse(json.dumps(responsedict), mimetype="application/json")


				
class HomeView(TemplateView):
    template_name = 'home.html'
    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        # homepage background image clickable section
        fadd = AddonType.objects.get(name__iexact='Custom Skin On Homepage')
        allskins = AddonCharge.objects.filter(
            addon=fadd,
            mixtape__approved=True
            ).prefetch_related()
        mixid_list = [g.object_id for g in allskins]
        obj_mix = Mixtape.objects.filter(approved=True, id__in=mixid_list).order_by('-id')
        for i in obj_mix:
            print i.id
            if i.id in mixid_list:
                m = Mixtape.objects.get(id=i.id)
                for obj in m.active_addons:
                    if obj.name == 'Custom Skin On Homepage':
                        today = datetime.now()
                        if obj.end_date>=today:
                            context['obj'] = m
                            break

        #b/w slider and spotlight section
	
        add_type = AddonType.objects.get(name__iexact='Enhanced Homepage Mixtape Countdown')
	all_comings = []
        all_coming = AddonCharge.objects.prefetch_related().filter(
                        Q(
                                addon=add_type,
                                end_datetime__gt=datetime.now(pytz.utc),
                                mixtape__approved=True
                        )
                        |
                        Q(
                                addon=add_type,
                                end_datetime=None,
                                mixtape__approved=True
                        )
                )
        
        if len(all_coming) >= 1:
                comings = random.sample(all_coming, len(all_coming))
#        else:
#                comings = all_coming
                if comings:
                        #Get the related mixtape objects
                        all_comings = [c.mixtape for c in comings]            
#        else:
#                #else take a random 6
#                all_comings = Mixtape.objects.filter(
#                                approved=True, releaseDatetime__gt=datetime.now(pytz.utc)
#                        ).order_by('-id')[:8]
        #cache.set('fp-coming', coming, 60*15)
                        
                        filter_all_comings = [c for c in all_comings if c.releaseDatetime > datetime.now(pytz.utc)]
                        context['all_comings'] = filter_all_comings
        #display_countdown_date = datetime.now()-timedelta(1)
	alert_cdown_list = [ m for m in all_comings if datetime.now(pytz.utc) > m.releaseDatetime-timedelta(1) and datetime.now(pytz.utc) < m.releaseDatetime]
	if alert_cdown_list:
		context['alert_cdown'] = random.choice(alert_cdown_list)
			
        #Front Page Slider
        slider = cache.get('fp-slider')
        if not slider:
        	sadd = AddonType.objects.get(name__iexact='Sitewide Slider Upgrade')
        	allslider = AddonCharge.objects.prefetch_related().filter(
        		addon=sadd,
        		end_datetime__gt=datetime.now(pytz.utc),
        		mixtape__approved=True,
        		mixtape__releaseDatetime__lt=datetime.now(pytz.utc)
        		)
        
        	#print '\n\nLENGTH OF ALLSLIDER IS %s' % len(allslider)
        
        	#Get the related mixtape objects
        	if allslider:
        		slider = [s.mixtape for s in allslider]
        
        	#If there are no mixtapes with this add-on... select a random up to 5
        	else:
        		slider = Mixtape.objects.filter(approved=True, releaseDatetime__lt=datetime.now(pytz.utc)).order_by('-id')[:5]
        
        	if len(slider) > 5:
        		slider = random.sample(slider, 5)
        
        	#print '\n\n\n\nTHERE ARE %s THINGS IN THE SLIDER!!!\n\n\n\n' % (len(slider))
        
        	#cache.set('fp-slider', slider, 60*15)
        context['slider'] = slider
        featured =[]
        #Front Feature
        #featured = cache.get('fp-featured')
        

        if not featured:
        	fadd = AddonType.objects.get(name__iexact='Featured Mixtape')
        	allfeatured = AddonCharge.objects.filter(
        		addon=fadd,
        		#end_datetime__gt=datetime.now(pytz.utc),
        		mixtape__approved=True
        		).prefetch_related()
		
        	if len(allfeatured) >= 12:
        		featured = random.sample(allfeatured, 12)
        	else:
        		featured = allfeatured
        
        	#print len(featured)
        	if featured:
        		#Get the related mixtape objects
        		mixid_list = [f.object_id for f in featured]
#        	else:
#        		#else take a random 12
#        		featured = Mixtape.objects.filter(approved=True).order_by('-id')[:12]
                featured_tapes = Mixtape.objects.filter(approved=True, id__in=mixid_list).order_by('-id')[:12]
        
        	#cache.set('fp-featured', featured, 60*15)
        context['featured'] = featured_tapes
        
        #genres = set([f.primaryGenre.name for f in featured])
        #context['featured_genres'] = genres
        
        #Front Coming Soon
        #coming = cache.get('fp-coming')
	coming = ""
        if not coming:
        	cadd = AddonType.objects.get(name__iexact='Enhanced Homepage Mixtape Countdown')
                caff = AddonType.objects.get(name__iexact='Basic Mixtape Page Countdown')
        	allcoming = AddonCharge.objects.prefetch_related().filter(
        			Q(
        				addon=cadd,
        				end_datetime__gt=datetime.now(pytz.utc),
        				mixtape__approved=True
        			)
        			|
        			Q(
        				addon=cadd,
        				end_datetime=None,
        				mixtape__approved=True
        			)
                                |
                                Q(
        				addon=caff,
        				end_datetime__gt=datetime.now(pytz.utc),
        				mixtape__approved=True
        			)
                                |
                                Q(
        				addon=caff,
        				end_datetime=None,
        				mixtape__approved=True
        			)
        		)
        	if len(allcoming) >= 6:
        		coming = random.sample(allcoming, 6)
        	else:
        		coming = allcoming
        	if coming:
        		#Get the related mixtape objects
        		coming = [c.mixtape for c in coming]
#        	else:
#        		#else take a random 6
#        		coming = Mixtape.objects.filter(
#        				approved=True, releaseDatetime__gt=datetime.now(pytz.utc)
#        			).order_by('-id')[:12]
	else:
		coming = Mixtape.objects.filter(
				        approved=True, releaseDatetime__gt=datetime.now(pytz.utc)
				    ).order_by('-id')[:8]		
        #coming = Mixtape.objects.filter(approved=True, id__in=mixid_list).order_by('-id')
        #cache.set('fp-coming', coming, 60*15)
	coming = set(coming)

        context['coming'] = [ x for x in iter(coming) ] 
        coming = [g.object_id for g in allcoming]
        #print coming
        context['countdown_home'] = Mixtape.objects.filter(approved=True, id__in=coming).order_by('-id')[:8]
        fadd = AddonType.objects.get(name__iexact='Custom Skin On Homepage')
        allskins = AddonCharge.objects.filter(
            addon=fadd,
            mixtape__approved=True
            ).prefetch_related()
        #print len(featured)

        try:
                upcoming = Mixtape.objects.filter(
				        approved=True, releaseDatetime__gt=datetime.now(pytz.utc)
				    ).order_by('-id')[:5]
                context['upcoming'] = upcoming
        except:
                context['upcoming'] = []
                pass
       
        
        if allskins:
            context['home_skin'] =False
            context['home_skin_url'] =''
            #Get the related mixtape objects
            #alladdons = [f.mixtape for f in alladdons]
            mix_ids = [g.object_id for g in allskins]
            obj_mix = Mixtape.objects.filter(approved=True, id__in=mix_ids).order_by('-id')
            
            for i in obj_mix:
                if i.id in mix_ids:
                    m=Mixtape.objects.get(id=i.id)
                    for ao in m.active_addons:
                        if ao.name == 'Custom Skin On Homepage':
                            today = datetime.now()
                            if ao.end_date>=today:
                                context['home_skin']= True
                                try:
                                    context['home_skin_url'] =m.images.filter(order=2).latest('id')
                                except:
                                    context['home_skin_url'] = ''
                                break

        dict = {}
        tap_list = []
        start_date =  datetime.now() - timedelta(30)
        context['topofmonth'] = Mixtape.objects.filter(approved=True,created__gt=start_date,created__lt=datetime.now(pytz.utc)).exclude(releaseDatetime__gt=datetime.now(pytz.utc)).order_by('-id')[:12]
        for obj in context['topofmonth']:
            dict[obj.id] = len(obj.pageview.all())
        key_list = sorted(dict.items(), key=lambda x: x[1], reverse=True)
        id_list = [i[0] for i in key_list]
        for obj_id in id_list:
            tap_list.append(Mixtape.objects.get(id=obj_id))
        context['topofmonth'] = tap_list
        #popular of last week
        start = timezone.now()-timedelta(7)
        mixtapes = [mixtapes.mixtape.id for mixtapes in MixtapePageView.objects.filter(mixtape__approved =True,date__gt=start,date__lt=datetime.now()).order_by('-id')]
            
        context['popularmixtapes']  = [mixtape for mixtape in Mixtape.objects.filter(id__in=set(mixtapes),approved=True,created__gt=start,releaseDatetime__lt = datetime.now())][:12]
        		
        #Recent, approved mixtapes
        context['recentmixtapes'] = Mixtape.objects.filter(approved=True, releaseDatetime__lt = datetime.now()).order_by('-id')[:12]
        try:
            context['spotlight'] = MixtapeSpotLight.objects.all()[0]
        except:
            pass
        return context

		
class UserProfileListView(ListView):
        model = UserProfile
        template_name = 'core/userprofile_list.html'

	def get_context_data(self, **kwargs):
		context = super(UserProfileListView, self).get_context_data(**kwargs)
		user_list = UserProfile.objects.all()
		context['users'] = user_list
		return context


class AutocompleteUserProfileViewSet(PreSaveMixin, viewsets.ModelViewSet):
        queryset = UserProfile.objects.all()
        serializer_class = UserProfileSerializer

        def get_queryset(self):
                ups = cache.get('ups')

                if not ups:
                        print '\nNOT IN THE CACHE!\n'
                        ups = UserProfile.objects.all()
                        cache.set('ups', ups)

                if self.request.GET['q']:
                        query = self.request.GET['q'].lower()
                        ups = filter(lambda x: re.search(query, x.username.lower()), ups)

                return ups
            
            
            
class AutocompleteTrackViewSet(PreSaveMixin, viewsets.ModelViewSet):
        queryset = Track.objects.all()
        serializer_class = MixtapeTrackSerializer

        def get_queryset(self):


                if self.request.GET['q']:
                        query = self.request.GET['q'].lower()
                        ups = Track.objects.all()
                        ups = filter(lambda x: re.search(query, x.filename.lower()), ups)
                return ups            

class MixtapeUploadView(LoginRequiredMixin, TemplateView):
    template_name = 'mixtape/mixtape_upload.html'
    def dispatch(self, request, *args, **kwargs):
        if self.kwargs['mixtapeid']:
        	exists = Mixtape.objects.filter(id=self.kwargs['mixtapeid']).exists()
        
        	if exists:
        
        		instance = Mixtape.objects.get(id=self.kwargs['mixtapeid'])
        
        		if instance.created_by == self.request.user:
        
        			if instance.releaseDatetime and instance.tracks.exists():
        				diff = datetime.now() - instance.releaseDatetime.replace(tzinfo=None)
        
        				if diff.days <= 2:
        					return super(MixtapeUploadView, self).dispatch(request, *args, **kwargs)
        
        				else:
        					messages.error(self.request, 'Mixtape can not be edited after 48 hours of release')
        					return redirect('/my-mixtapes')
        
        			else:
        				return super(MixtapeUploadView, self).dispatch(request, *args, **kwargs)
        
        		#If the requesting user is not the artist, return to the regular upload page
        		else:
        			return redirect(reverse('mixtape_create', kwargs={'mixtapeid':''}))
        
        	else:
        		return redirect(reverse('mixtape_create', kwargs={'mixtapeid':''}))
        
        else:
        	# If requesting user has mixtapes with no tracks, redirect to edit last of them
        	# Somewhy this gets executed for non-logged-in user, causing exception and breaking login redirect, so we have to check auth
        	if self.request.user.is_authenticated():
        		empty_mixtapes = Mixtape.objects.filter(created_by=self.request.user, tracks=None)
        		if empty_mixtapes:
        			return redirect(reverse('mixtape_create', kwargs={'mixtapeid':empty_mixtapes[0].id}))
        	return super(MixtapeUploadView, self).dispatch(request, *args, **kwargs)
	
	
    def get_context_data(self, **kwargs):
        context = super(MixtapeUploadView, self).get_context_data(**kwargs)
        
        if self.kwargs['mixtapeid']:
        	instance = Mixtape.objects.get(id = self.kwargs['mixtapeid'])
        else:
        	instance = None
        
        if instance:
        	mtform = MixtapeCreateForm(initial={'name':instance.name, 'video_url':instance.video_url, 'releaseDatetime':instance.releaseDatetime, 'primaryGenre':instance.primaryGenre.id})
        	context['instance'] = instance
        else:
        	mtform = MixtapeCreateForm()
        
        context['mixtape_create_form'] = mtform
        context['userprofile_create_form'] = UserProfileCreateForm
        context = super(MixtapeUploadView, self).get_context_data(**kwargs)
        genres = cache.get('all_genres')
        if not genres:
		genres = Genre.objects.values('id', 'name')
		cache.set('all_genres', genres)
        context['genres'] = genres			
        context['artists'] = User.objects.all()
        context['mixtape_uploads'] = True
	context['mixtape'] = instance
        try:
            subscription = self.request.user.customer.has_active_publisher_subscription()
        except:
            subscription = False
        if not subscription:
            mixtape_uploads = Mixtape.objects.filter( created_by = self.request.user).count()
            if mixtape_uploads >=3:
                context['mixtape_uploads'] = False
        return context
	

class MixtapesListView(ListView):
    model = Mixtape
    template_name = 'mixtape/mixtape_list.html'
    queryset = Mixtape.objects.all().filter(approved=True)#, releaseDatetime__lt=datetime.datetime.now(pytz.utc))    

    def get_context_data(self, **kwargs):
        context = super(MixtapesListView, self).get_context_data(**kwargs)
        queryset = Mixtape.objects.all().filter(approved=True, releaseDatetime__lt=datetime.datetime.now(pytz.utc))
        context['object_list'] = queryset
        history = queryset
        paginator = Paginator(history, 40) # Show 25 contacts per page
        page = self.request.GET.get('page')
        try:
            history = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            history = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            history = paginator.page(paginator.num_pages)

        context['object_list'] = history
        return context
        
class MixtapeCreateView(JSONResponseMixin, AjaxResponseMixin, View):
    def get(self,request,*args, **kwargs):
	responsedict = {}
	mixtape_id = self.kwargs['mixtapeid']
	mixtape_obj = Mixtape.objects.get(id=mixtape_id)
	responsedict['success'] = True
	responsedict['current_mixtape_id'] = mixtape_obj.id
	responsedict['current_mixtape_content_type_id'] = mixtape_obj.get_content_type_id()
	responsedict['mixtapeid'] = mixtape_obj.id
	responsedict['content_type_id'] = mixtape_obj.get_content_type_id()	
	return HttpResponse(json.dumps(responsedict), mimetype="application/json")    
		
    def post(self, request, *args, **kwargs):
	  
        data = request._post
        responsedict = {}
	mixtape_id = self.kwargs['mixtapeid']
	if mixtape_id:
	    try:
		mixtape_obj = Mixtape.objects.get(id=mixtape_id)
		try:
			genre = Genre.objects.get(id=data['primaryGenre'])
		except:
			genre = ''
		try:
			artist = UserProfile.objects.get(user__username=data['primaryArtist'])
		except:
			artist = ''
		try:
			secondaryartist = UserProfile.objects.get(user__username=data['secondaryartist'])
		except:
			secondaryartist = None
		try:
			djs = UserProfile.objects.get(user__username=data['djs'])
		except:
			djs = None
		try:
			producer = UserProfile.objects.get(user__username=data['producer'])
		except:
			producer = None
		#djs = User.objects.get(id=data['djs'])
		mixtape_obj.slug=slugify(data['name'])
		mixtape_obj.name = data['name']
		mixtape_obj.description =data['description']
		mixtape_obj.primaryGenre=genre
		mixtape_obj.primaryArtist=artist
		mixtape_obj.updated_by=request.user
		mixtape_obj.video_url=data['video_url']
		mixtape_obj.djs = djs
		mixtape_obj.producer = producer
		mixtape_obj.secondaryArtist = secondaryartist
		mixtape_obj.save()
		responsedict['success'] = True
		responsedict['mixtapeid'] = mixtape_obj.id
		responsedict['full_mixtape_slug'] = slugify(mixtape_obj.full_mixtape_slug)
		responsedict['content_type_id'] = mixtape_obj.get_content_type_id()
		responsedict['current_mixtape_id'] = mixtape_obj.id
		responsedict['current_mixtape_content_type_id'] = mixtape_obj.get_content_type_id()			
	   
	    except Exception,e:
			print e
			responsedict['success'] = False
		
	else:
		try:
			try:
				genre = Genre.objects.get(id=data['primaryGenre'])
			except:
				genre = ''
			try:
				artist = UserProfile.objects.get(id=data['primaryArtist'])
			except:
				artist = ''
			try:
				secondaryartist = UserProfile.objects.get(id=data['secondaryartist'])
			except:
				secondaryartist = None
			try:
				djs = UserProfile.objects.get(id=data['djs'])
			except:
				djs = None
			try:
				producer = UserProfile.objects.get(id=data['producer'])
			except:
				producer = None
			#djs = User.objects.get(id=data['djs'])
			slug=slugify(data['name'])
			date = data.get('release_datetime','').strip()
			if date:
				release_date = str(timezone.make_aware(datetime.strptime(date,'%d %B %Y - %H:%M'),timezone.get_default_timezone()))
			else:
				release_date = str(timezone.make_aware(datetime.now(),timezone.get_default_timezone()))
			mixtape_obj = Mixtape(name=data['name'],description =data['description'], 
			                      slug=slug,primaryGenre=genre,primaryArtist=artist,
			                      created_by = request.user,updated_by=request.user,
			                      video_url=data['video_url'],djs = djs,producer = producer,
			                      secondaryArtist = secondaryartist,releaseDatetime=release_date)
			
	    
			mixtape_obj.save()
			currentsite = get_current_site(request)
			#https://bitbucket.org/247mixtapes/247mixtapes/issue/173/user-channel-subscriptions
	    #             from django.utils.html import conditional_escape
	    #             from django.utils.safestring import mark_safe
	    #             for i in ArtistSubscription.objects.filter(artist = artist):
	    #                 message= mark_safe('Artist '+artist.username+' uploaded new mixtape. please check '+currentsite.domain+'/'+artist.username+'/'+data['name']+'/'+str(mixtape_obj.id))
	    #                 email_message = send_mail('Artist Newsletter',message,settings.DEFAULT_FROM_EMAIL,
	    #                                     [i.user.user.email], fail_silently=False) 
	    #                 print email_message
			responsedict['success'] = True
			responsedict['mixtapeid'] = mixtape_obj.id
			responsedict['full_mixtape_slug'] = slugify(mixtape_obj.full_mixtape_slug)
			responsedict['content_type_id'] = mixtape_obj.get_content_type_id()
			responsedict['current_mixtape_id'] = mixtape_obj.id
			responsedict['current_mixtape_content_type_id'] = mixtape_obj.get_content_type_id()				
					
		except Exception,e:
			print e
			responsedict['success'] = False
        return HttpResponse(json.dumps(responsedict), mimetype="application/json")
		
class MixtapeImageView(JSONResponseMixin, AjaxResponseMixin, View):
	
    def get(self,request,*args, **kwargs):
	responsedict = {}
	mixtape_id = self.kwargs['object_id']
	mixtape_obj = Mixtape.objects.get(id=mixtape_id)
	responsedict['success'] = True
	responsedict['current_mixtape_id'] = mixtape_obj.id
	responsedict['current_mixtape_content_type_id'] = mixtape_obj.get_content_type_id()
	responsedict['mixtapeid'] = mixtape_obj.id
	responsedict['content_type_id'] = mixtape_obj.get_content_type_id()	
	return HttpResponse(json.dumps(responsedict), mimetype="application/json")
		
    def post_ajax(self, request, *args, **kwargs):
        data = self.request._post

        # If url ends with image id, update it
        image_id = self.request.path.split('/')[-1]
        if image_id.isdigit():
            image_obj = Image.objects.filter(id=image_id)
            image_obj.update(order=int(data['order']), name=data['name'])
            return HttpResponse(json.dumps({'success': True}), mimetype="application/json")

        # Otherwise, create
    	responsedict = {}
    	#defaultpk = data['defaultimage']
    
    	try:
            if data['isWriteable'] == 'true':
            		is_writable = 1
            else:
            		is_writable = 0
            mixtape_obj = Mixtape.objects.get(id=data['mixtape'])
            image_obj = Image(url=data['url'], filename=data['filename'],mimetype=data['filename'],
            				  size=data['size'],isWriteable=is_writable, key=data['key'],object_id=data['object_id'],order=int(data['level']),
            				  content_type_id=mixtape_obj.get_content_type_id())
            image_obj.save()
            		
            #mixtape_obj.images = image_obj.object_id
            #mixtape_obj.save()
            responsedict['success'] = True
            responsedict['current_mixtape_id'] = mixtape_obj.id
            responsedict['current_mixtape_content_type_id'] = mixtape_obj.get_content_type_id()
    
    	except:
    			responsedict['success'] = False
    
    	return HttpResponse(json.dumps(responsedict), mimetype="application/json")

    def delete_ajax(self, request, *args, **kwargs):
        image_obj = Image.objects.get(id=self.request.path.split('/')[-1])
        image_obj.delete()
        return HttpResponse('')
		
class TrackListView(JSONResponseMixin, AjaxResponseMixin, View):
		
        def post_ajax(self, request, *args, **kwargs):
            responsedict = {}
            data = self.request._post
            #defaultpk = data['defaultimage']
            if self.request._post.get('artists','') !='':
                try:
                    try:
                        obj = UserProfile.objects.get(id=data['artists'])
                    except:
                        obj = UserProfile.objects.get(username=data['artists'])
                    track_id=int(data['track_id'])
                    objTrack=Track.objects.get(id=track_id)
                    objTrack.artists = str(obj.id)
                    if data['producers'] != '':
                        try:
                            obj1 = UserProfile.objects.get(id=data['producers'])
                        except:
                            obj1 = UserProfile.objects.get(username=data['producers'])
                        objTrack.producers = str(obj1.id)
                    else:
                        objTrack.producers = ''
                    if data['producers'] != '':
                        try:
                            obj2 = UserProfile.objects.get(id=data['djs'])
                        except:
                            obj2 = UserProfile.objects.get(username=data['djs'])
                        objTrack.djs = str(obj2.id)
                    else:
                        objTrack.djs = ''
                    objTrack.name = data['name']
                    objTrack.filename = data['name']
                    objTrack.lyrics = data['lyrics']
                    objTrack.order = data['order']
                    objTrack.save()
                    responsedict['success'] = True
                except Exception,e:
                    print e
                    responsedict['success'] = False

            elif data['order']:
                try:
#                    try:
#                        obj = UserProfile.objects.get(id=data['artists'])
#                    except:
#                        obj = UserProfile.objects.get(username=data['artists'])
                    track_id=int(data['track_id'])
                    objTrack=Track.objects.get(id=track_id)
#                    objTrack.artists = str(obj.id)
                    if data['producers'] != '':
                        try:
                            obj1 = UserProfile.objects.get(id=data['producers'])
                        except:
                            obj1 = UserProfile.objects.get(username=data['producers'])
                        objTrack.producers = str(obj1.id)
                    else:
                        objTrack.producers = ''
                    if data['producers'] != '':
                        try:
                            obj2 = UserProfile.objects.get(id=data['djs'])
                        except:
                            obj2 = UserProfile.objects.get(username=data['djs'])
                        objTrack.djs = str(obj2.id)
                    else:
                        objTrack.djs = ''
                    objTrack.name = data['name']
                    objTrack.filename = data['name']
                    objTrack.lyrics = data['lyrics']
                    objTrack.order = data['order']
                    objTrack.save()
                    responsedict['success'] = True
                except Exception,e:
                    print e
                    responsedict['success'] = False

            else:
                try:
                    if data['isWriteable'] == 'true':
                            is_writable = 1
                    else:
                            is_writable = 0        
                    mixtape_obj = Mixtape.objects.get(id=data['mixtape'])
	            track_obj = track_obj = Track(mixtape=mixtape_obj,url=data['url'],filename=data['filename'],mimetype=data['mimetype'],isWriteable=is_writable,size=data['size'],key=data['key'])
                    track_obj.save()
                    responsedict['id'] = track_obj.id
                    responsedict['url'] = str(mixtape_obj.addons_url())
                    #mixtape_obj.images = image_obj.object_id
                    #mixtape_obj.save()
                    responsedict['success'] = True
                except:
                    responsedict['success'] = False
            return HttpResponse(json.dumps(responsedict), mimetype="application/json")
		
        def delete_ajax(self, request, *args, **kwargs):
            track_obj = Track.objects.get(id=self.request.path.split('/')[-1])
            track_obj.delete()
            return HttpResponse('')

class NotifyAdminView(LoginRequiredMixin, AjaxResponseMixin, JSONResponseMixin, View):
        def post_ajax(self, request, *args, **kwargs):
				data = self.request._post
				mixtapeid = data['mixtape_id']
				responsedict = {}
				#currentsite = get_current_site(request)

				try:
						mt = Mixtape.objects.get(id=mixtapeid)
						sendNotifyAdminEmail(mt)#.delay()
						responsedict['success'] = True
				except:
						responsedict['success'] = False

				return HttpResponse(json.dumps(responsedict), mimetype="application/json")



from rest_framework import viewsets
from rest_framework.decorators import link, action
# action = POST, link = GET

class PreSaveMixin(object):
		def pre_save(self, obj):
				obj.slug = slugify(obj.name)
				obj.created_by = self.request.user
		
class MixtapeImageViewSet(PreSaveMixin, viewsets.ModelViewSet):
        queryset = Image.objects.all()
        serializer_class = MixtapeImageSerializer
        filter_fields = ('mixtape',)
		
class TrackViewSet(viewsets.ModelViewSet):
        queryset = Track.objects.all()
        serializer_class = TrackSerializer
        filter_fields = ('mixtape',)
		
class UserProfileListView(ListView):
    model = UserProfile
    template_name = 'mixtape/userprofile_list.html'
    
    def get_context_data(self, **kwargs):
        context = super(UserProfileListView, self).get_context_data(**kwargs)
        user_list = UserProfile.objects.all()
        history = user_list
        paginator = Paginator(history, 40) # Show 25 contacts per page
        
        page = self.request.GET.get('page')
        try:
            history = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            history = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            history = paginator.page(paginator.num_pages)
        
        context['users'] = history
        return context


class DownloadView(View):

    def get(self, request, *args, **kwargs):
        mixtape_obj = Mixtape.objects.get(id=self.kwargs['mixtapeid'])
        download_files = mixtape_obj.downloadTracks(mixtape_obj,request)
        if mixtape_obj.soundcloud_playback_count == None:
            playback_count= 0
        else:
            playback_count = mixtape_obj.soundcloud_playback_count
        mixtape_obj.soundcloud_playback_count = playback_count +1
        mixtape_obj.save()
        response = HttpResponse(mimetype='application/zip')
        response['Content-Disposition'] = ('attachment; '
                                        'filename=' + mixtape_obj.fullAlbumName)		
        files = []
        folder = settings.TEMP_ROOT+'/'+mixtape_obj.fullAlbumName
        for f in os.listdir(folder):
        	files.append(folder+'/'+f)
        buffer = StringIO()
        zip = zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED)
        for f in files:
        	filename = os.path.basename(f)
        	zip.write(f,filename)
        zip.close()
        buffer.flush()
        #the import detail--we return the content of the buffer
        ret_zip = buffer.getvalue()
        buffer.close()
        response.write(ret_zip)	
        temproot = settings.TEMP_ROOT
        mixtaperoot = os.path.join(temproot, mixtape_obj.fullAlbumName)
        #Check if it already exists, if so, delete it and start anew
        if os.path.isdir(mixtaperoot):
            print '\t--> Deleting existing directory with the same name!'
            shutil.rmtree(mixtaperoot)
        return response
		
class UserProfileDetailView(ListView):
        model = UserProfile
        template_name = 'mixtape/userprofile_detail.html'

        def get_context_data(self, **kwargs):
                context = super(UserProfileDetailView, self).get_context_data(**kwargs)
		try:
			obj = UserProfile.objects.get(user__username=self.kwargs['slug'])
		except:
			obj = UserProfile.objects.get(slug=self.kwargs['slug'])
                obj.views= obj.views+1
                obj.save()
                context['obj'] = obj
		try:
			from mixtape.models import GoogleAdsBlock
			googleads_user = GoogleAdsBlock.objects.all()
			if googleads_user:
				context['ads_user'] = googleads_user[0]
		except:
			pass
			
                if self.request.user.is_authenticated():
                    try:
                        context['subscribe'] = ArtistSubscription.objects.get(user=self.request.user.userprofile,artist = obj)
                    except:
                         context['subscribe']=[]
                featured = Mixtape.objects.filter(primaryArtist=obj,approved=True).order_by('-created').prefetch_related()
                context['featured'] = featured
                
                produced = obj.producer_tracks.order_by('-created').prefetch_related()
                context['produced'] = produced
                obj_count= Mixtape.objects.filter(primaryArtist__username=self.kwargs['slug'])
                d_count=0
                s_count=0
                for i in obj_count:
                    if i.soundcloud_playback_count !=None:
                        d_count+=i.soundcloud_playback_count
                    if i.soundcloud_favoritings_count !=None:
                        s_count+=i.soundcloud_favoritings_count
                context['d_count'] = d_count
                context['s_count'] = s_count
                #mixtapesview = MixtapePageView.objects.filter(mixtape__primaryArtist__username=self.kwargs['slug'])
                #print mixtapesview,d_count
                context['profileviews'] = obj.views
                djed = obj.dj_tracks.order_by('-created').prefetch_related()
                context['djed'] = djed
                
                history = Mixtape.objects.filter(primaryArtist=obj,approved=True).order_by('-id')
        
                
        
                paginator = Paginator(history, 40) # Show 25 contacts per page
            
                page = self.request.GET.get('page')
                try:
                    history = paginator.page(page)
                except PageNotAnInteger:
                    # If page is not an integer, deliver first page.
                    history = paginator.page(1)
                except EmptyPage:
                    # If page is out of range (e.g. 9999), deliver last page of results.
                    history = paginator.page(paginator.num_pages)
                context['recentmixtapes'] =history
                
                
                
                
                published = Track.objects.filter(created_by=obj).order_by('-created').prefetch_related()
                context['published'] = published
                if self.kwargs['slug']:
                    context['current_user'] = self.kwargs.get('slug', '')
                return context

class MixtapeAddonViewSet(viewsets.ModelViewSet):
        queryset = AddonType.objects.all()
        serializer_class = MixtapeAddonSerializer

class AboutUsView(TemplateView):
        template_name = 'mixtape/aboutus.html'
        
class TrackView(AjaxResponseMixin, JSONResponseMixin, View):
        def post_ajax(self, request, *args, **kwargs):
                data = self.request._post
                responsedict = {}
                try:
		
			mixtape_obj = Mixtape.objects.get(id=data['id'])
			if data['event'] == 'download':
				if mixtape_obj.soundcloud_playback_count != None:
					count =  mixtape_obj.soundcloud_playback_count
				else:
					count = 0
				mixtape_obj.soundcloud_playback_count = count +1
			else:
				if mixtape_obj.soundcloud_favoritings_count != None:
					count =  mixtape_obj.soundcloud_favoritings_count
				else:
					count = 0
				mixtape_obj.soundcloud_favoritings_count = count +1
                        
			mixtape_obj.save()     
			responsedict['count'] = count +1           
			responsedict['success'] = True
                except Exception as e:
			print e
			responsedict['success'] = False
			responsedict['count'] = 0
                return HttpResponse(json.dumps(responsedict), mimetype="application/json")



class SignedUrlView(AjaxResponseMixin, JSONResponseMixin, View):
        def post_ajax(self, request, *args, **kwargs):

                data = self.request._post
                responsedict = {}
		
                try:     
			if data['event'] == 'aws_url':
				track_obj = data['url']
				id = data['id']
				
				# TODO: use cdn url from settings
				if track_obj.startswith('https://cdn.247mixtapes.com/') or track_obj.startswith('http://cdn.247mixtapes.com/'):
					track_url = track_obj
					secs = 180
					signed_url = get_signed_url(track_url,track_url,secs)
				else:
					signed_url = track_obj
					
				responsedict['url'] = signed_url
				responsedict['id'] = id
				responsedict['success'] = True
				
			if data['event'] == 'signed_url':
				track_obj = data['url']
				
				if track_obj.startswith('https://cdn.247mixtapes.com/') or track_obj.startswith('http://cdn.247mixtapes.com/'):
					track_url = track_obj.split('?')[0]
					secs = 180
					signed_url = get_signed_url(track_url,track_url,secs)
				else:
					signed_url = track_obj
					
				responsedict['url'] = signed_url
				responsedict['success'] = True
				
		
		except Exception as e:
			print e
			responsedict['success'] = False
			
		return HttpResponse(json.dumps(responsedict), mimetype="application/json")		
		


		
class FeaturedMixtapView(ListView):
    model = Mixtape
    template_name = 'mixtape/featured_mixtapes.html'
    		
    def get_context_data(self, **kwargs):
        context = super(FeaturedMixtapView, self).get_context_data(**kwargs)
        		
        fadd = AddonType.objects.get(name__iexact='Featured Mixtape')
        featured = AddonCharge.objects.filter(
        		                addon=fadd,
	                        #end_datetime__gt=datetime.now(pytz.utc),
        		                mixtape__approved=True
        		                ).prefetch_related()
        mixid_list = [g.object_id for g in featured]
        #featured = [f.mixtape for f in featured]
        featured = Mixtape.objects.filter(approved=True, id__in=mixid_list).order_by('-id')
        context['object_list'] = featured
        history = featured
        paginator = Paginator(history, 40) # Show 25 contacts per page
        page = self.request.GET.get('page')
        try:
            history = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            history = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            history = paginator.page(paginator.num_pages)
        context['object_list'] = history
        if featured:
            context['featured'] = featured[0]
            context['object'] = featured[0]
        
        return context


class HotMixtapView(ListView):
        model = Mixtape
        template_name = 'mixtape/hot_this_week.html'
                
        def get_context_data(self, **kwargs):
                context = super(HotMixtapView, self).get_context_data(**kwargs)
                mixtapes = [mixtapes.mixtape for mixtapes in MixtapePageView.objects.filter(mixtape__approved = True,date__gt=start,date__lt=datetime.now())]
                context['object_list']  = [mixtape for mixtape in set(mixtapes)][:12]   
                fadd = AddonType.objects.get(name__iexact='Featured Mixtape')
                featured = AddonCharge.objects.filter(
                                        addon=fadd,
                                        mixtape__approved=True
                                        ).prefetch_related()     
                featured = [f.mixtape for f in featured]                
                if featured:
                    context['featured'] = featured[0]
                    context['object'] = featured[0]
                return context
						
class RecentMixtapView(ListView):
    model = Mixtape
    template_name = 'mixtape/recent_mixtapes.html'
    		
    def get_context_data(self, **kwargs):
        context = super(RecentMixtapView, self).get_context_data(**kwargs)
        genre =self.request.GET.get('genre','')
        
        if genre != '':
            genre = Genre.objects.get(slug=genre)
            object_list = Mixtape.objects.filter(primaryGenre = genre,approved=True,releaseDatetime__lt=datetime.now(pytz.utc)).order_by('-id')[:40]
        else:
            
            object_list = Mixtape.objects.filter(approved=True, releaseDatetime__lt=datetime.now(pytz.utc)).order_by('-id')[:40]
        context['object_list'] = object_list
        history = object_list
        paginator = Paginator(history, 40) # Show 25 contacts per page
        page = self.request.GET.get('page')
        try:
            history = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            history = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            history = paginator.page(paginator.num_pages)

        context['tap_list'] = history
        return context


class HotThisWeekMixtapView(ListView):
    model = Mixtape
    template_name = 'mixtape/hot_this_week.html'
    		
    def get_context_data(self, **kwargs):
    	context = super(HotThisWeekMixtapView, self).get_context_data(**kwargs)
    	start = datetime.now()-timedelta(7)
    	mixtapes = [mixtapes.mixtape.id for mixtapes in MixtapePageView.objects.filter(mixtape__approved=True,date__gt=start,date__lt=datetime.now()).order_by('-id')]
    	context['object_list']  = [mixtape for mixtape in Mixtape.objects.filter(id__in=set(mixtapes),approved=True,created__gt=start)][:12]
        fadd = AddonType.objects.get(name__iexact='Featured Mixtape')
        featured = AddonCharge.objects.filter(
                                addon=fadd,
                                mixtape__approved=True
                                ).prefetch_related()     
        featured = [f.mixtape for f in featured]
        history = context['object_list']
        paginator = Paginator(history, 40) # Show 25 contacts per page
        page = self.request.GET.get('page')
        try:
            history = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            history = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            history = paginator.page(paginator.num_pages)
        context['object_list'] = history
        if featured:
            context['featured'] = featured[0]
            context['object'] = featured[0]
        return context
    

class TopOfMonthMixtapView(ListView):
    model = Mixtape
    template_name = 'mixtape/top_of_month.html'
            
    def get_context_data(self, **kwargs):
        dict = {}
        tap_list = []
        context = super(TopOfMonthMixtapView, self).get_context_data(**kwargs)
        start = datetime.now()-timedelta(7)
        mixtapes = [mixtapes.mixtape for mixtapes in MixtapePageView.objects.filter(mixtape__approved=True,date__gt=start,date__lt=datetime.now()).order_by('-id')]
        start_date =  datetime.now() - timedelta(30)
        context['object_list'] = Mixtape.objects.filter(approved=True,created__gt=start_date,created__lt=datetime.now(pytz.utc)).exclude(releaseDatetime__gt=datetime.now(pytz.utc))[:8]
        for obj in context['object_list']:
            dict[obj.id] = len(obj.pageview.all())
        key_list = sorted(dict.items(), key=lambda x: x[1], reverse=True)
        id_list = [i[0] for i in key_list]
        for obj_id in id_list:
            tap_list.append(Mixtape.objects.get(id=obj_id))
        context['object_list'] = tap_list
        fadd = AddonType.objects.get(name__iexact='Featured Mixtape')
        featured = AddonCharge.objects.filter(
                                addon=fadd,
                                mixtape__approved=True
                                ).prefetch_related()     
        featured = [f.mixtape for f in featured]
        history = context['object_list']
        paginator = Paginator(history, 40) # Show 25 contacts per page
        page = self.request.GET.get('page')
        try:
            history = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            history = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            history = paginator.page(paginator.num_pages)
        context['object_list'] = history
        if featured:
            context['featured'] = featured[0]
            context['object'] = featured[0]
        return context
    

class UpcomingMixtapView(ListView):
    model = Mixtape
    template_name = 'mixtape/upcoming.html'
            
    def get_context_data(self, **kwargs):
        context = super(UpcomingMixtapView, self).get_context_data(**kwargs)
        start = datetime.now()-timedelta(7)
        coming = cache.get('fp-coming')
        if not coming:
            cadd = AddonType.objects.get(name__iexact='Enhanced Homepage Mixtape Countdown')
            caff = AddonType.objects.get(name__iexact='Basic Mixtape Page Countdown')
            allcoming = AddonCharge.objects.prefetch_related().filter(
                    Q(
                        addon=cadd,
                        end_datetime__gt=datetime.now(pytz.utc),
                        mixtape__approved=True
                    )
                    |
                    Q(
                        addon=cadd,
                        end_datetime=None,
                        mixtape__approved=True
                    )
                    |
                    Q(
                        addon=caff,
                        end_datetime__gt=datetime.now(pytz.utc),
                        mixtape__approved=True
                    )
                    |
                    Q(
                        addon=caff,
                        end_datetime=None,
                        mixtape__approved=True
                    )

                )
            if len(allcoming) >= 6:
                coming = random.sample(allcoming, 6)
            else:
                coming = allcoming
        
            if coming:
                #Get the related mixtape objects
                coming = [c.mixtape for c in coming]
            else:
                #else take a random 6
                coming = Mixtape.objects.filter(
                        approved=True, releaseDatetime__gt=datetime.now(pytz.utc)
                    ).order_by('-id')[:12]
        #cache.set('fp-coming', coming, 60*15)
	coming = set(coming)
        context['object_list'] = [ x for x in iter(coming) ]
        fadd = AddonType.objects.get(name__iexact='Featured Mixtape')
        featured = AddonCharge.objects.filter(
                                addon=fadd,
                                mixtape__approved=True
                                ).prefetch_related()     
        featured = [f.mixtape for f in featured]
        history = context['object_list']
        paginator = Paginator(history, 40) # Show 25 contacts per page
        page = self.request.GET.get('page')
        try:
            history = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            history = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            history = paginator.page(paginator.num_pages)
        context['object_list'] = history
        if featured:
            context['featured'] = featured[0]
            context['object'] = featured[0]
        
        
        return context
						

class SignupView(FormView):
		model = User
		template_name = "account/signup.html"
		form_class = SignupForm
		redirect_field_name = "next"
		success_url = None
	
		#def get_form_class(self):
			#return get_form_class(app_settings.FORMS, 'signup', self.form_class)
	
		def get_success_url(self):
			# Explicitly passed ?next= URL takes precedence
			context = (get_next_redirect_url(self.request,
							             self.redirect_field_name)
				   or self.success_url)
			return context
	
		def form_valid(self, form):
				user = form.save(self.request)
				#client = TwilioRestClient(settings.TWILIO_ACCOUNT, settings.TWILIO_TOKEN)
				#text_message = "please enter enter 1 as your verification code"
				#message = client.messages.create(
						    #to='+12244196359',
						    #from_=settings.TWILIO_NUMBER,
						    #body=text_message
						    #)
				#if message.sid:
						#self.request.session['signupform'] = form
						##self.request.session['user'] = user
												
						#return HttpResponseRedirect('/twilio_verification/')		
				
				#user_obj = complete_signup(self.request, user,
							       #app_settings.EMAIL_VERIFICATION,
							       #'/twilio_verification/')
				#twilio_obj = TwilioVerification(to=form.data['cell_phone'],from_=settings.TWILIO_NUMBER, body=text_message,content_type_id=14,object_id=12)
				#twilio_obj.save()
				#twilio_obj.send_text()
				#return HttpResponseRedirect('/twilio_verification/')

				#user = form.save(self.request)
				#return complete_signup(self.request, user,
							       #app_settings.EMAIL_VERIFICATION,
							       #self.get_success_url())

                def render_to_response(self, context, **response_kwargs):
                                """
                                Returns a response, using the `response_class` for this
                                view, with a template rendered with the given context.
                                If any keyword arguments are provided, they will be
                                passed to the constructor of the response class.
                                """
                                response = super(SignupView, self).render_to_response(context, **response_kwargs)
                                response.set_cookie("plan", self.request.REQUEST.get('plan'))
                                response.set_cookie("flag", "True")
                                return response
                                
	
		def get_context_data(self, **kwargs):
				form = self.form_class()
				form.fields["email"].initial = self.request.session \
						    .get('account_verified_email', None)
				#ret = super(SignupView, self).get_context_data(**kwargs)
				context = super(SignupView, self).get_context_data(**kwargs)
								
				redirect_field_name = self.redirect_field_name
				redirect_field_value = self.request.REQUEST.get(redirect_field_name)
				context.update({"login_url": '/login/',
						            "redirect_field_name": redirect_field_name,
						            "redirect_field_value": redirect_field_value})
				return context



class TwilioVerificationView(AjaxResponseMixin, JSONResponseMixin, View):
        def post_ajax(self, request, *args, **kwargs):
                                if request.user.is_authenticated():
                                    data = self.request._post.copy()
                                    test = UserProfile.objects.get(user=request.user.pk)
                                    data.update({'cell_phone':test.cell_phone})
                                else:
                                    data = self.request._post
				responsedict = {}

				try:
						client = TwilioRestClient(settings.TWILIO_ACCOUNT, settings.TWILIO_TOKEN)
						verication_text = randint(10000,99999) 
						text_message = "Use "+str(verication_text)+" as your cell phone verification number for 247Mixtapes.com"
						message = client.messages.create(
									to=data['cell_phone'],
									from_=settings.TWILIO_NUMBER,
									body=text_message
									)
						responsedict['message'] = message.sid
						responsedict['form_data'] = data
						responsedict['message_body'] = text_message
						responsedict['verication_text'] = verication_text
                                                if request.user.is_authenticated():
						    test_usr = UserProfile.objects.get(user=request.user.pk)
                                                    test_usr.verify_code = verication_text;
                                                    test_usr.save()
						responsedict['success'] = True
				except:
						#messages.info(self.request, 'Unable to send verification text to your given cell phone. Please try again')
						responsedict['message_info'] = 'Unable to send verification text to your given cell phone. Please try again'
						responsedict['success'] = False

				return HttpResponse(json.dumps(responsedict), mimetype="application/json")
						
  
class AddArtistView(AjaxResponseMixin, JSONResponseMixin, View):
        def post_ajax(self, request, *args, **kwargs):
                data = self.request._post
                responsedict = {}
                user_obj = ''
                try:
                    user = User.objects.filter(username__iexact=data['username'])[0]
                except Exception as e:                  
                    user = None
                try:
                        if user == None:
                            user_obj = User.objects.create_user(username=data['username'])
                            user_obj.is_active = True
                            user_obj.save()
                                                
                        userprofile_obj = user_obj.userprofile
                        userprofile_obj.facebook = data['facebook']
                        userprofile_obj.twitter = data['twitter']
                        userprofile_obj.google = data['google']
                        userprofile_obj.youtube = data['youtube']
                        userprofile_obj.pinterest = data['pinterest']
                        userprofile_obj.soundcloud = data['soundcloud']
			userprofile_obj.slug = slugify(user_obj.username)
                        userprofile_obj.save()

                        responsedict['user_exist'] = True
                        responsedict['success'] = True
                except Exception as e:
                        print e
                        if data['username'] == '':
                            error_message = "This field is required"
                        else:
                            error_message = "This name already exists"
                        responsedict['error_message'] = error_message
                        responsedict['success'] = False
        
                return HttpResponse(json.dumps(responsedict), mimetype="application/json")                      
                        
class AddUserProfileView(AjaxResponseMixin, JSONResponseMixin, LoginRequiredMixin, View):

		def post_ajax(self, request, *args, **kwargs):
				data = self.request._post
				responsedict = {}
		         
				try:
						user_obj = User.objects.create_user(username=data['data[username][]'], email=data['data[email][]'])
						user_obj.set_password(data['data[password1][]'])
						user_obj.is_active = True
						user_obj.save()
												
						userprofile_obj = user_obj.userprofile
						userprofile_obj.cell_phone = data['data[cell_phone][]']
                                                userprofile_obj.phon_verified = True
                                                userprofile_obj.verify_code = data['code']
						userprofile_obj.save()
								
						#verify_obj = TwilioVerification(user=user_obj, to=data['data[cell_phone][]'],from_= settings.TWILIO_NUMBER,
												        #body=data['message_body'],sid=data['message'],
												        #content_type_id=user_obj.userprofile.get_content_type_id(),
												        #object_id=user_obj.userprofile.id, verified=True)
						#verify_obj.save
						new_user = authenticate(username=data['data[username][]'], password=data['data[password1][]'])
						login(self.request, new_user)
						messages.success(self.request,'Your account has now been created and verified. Welcome to 247Mixtapes.com!')
						#if data['data[email][]']:
						#		email_message = send_mail('Welcome to 24/7Mixtapes', 'Your account has now been created and verified. Welcome to 247Mixtapes.com!.', settings.DEFAULT_FROM_EMAIL,
						#			[data['data[email][]']], fail_silently=False)
						#complete_signup(self.request, user_obj, settings.ACCOUNT_EMAIL_VERIFICATION, settings.LOGIN_REDIRECT_URL)
						print 'Sending email confirmation'
						from allauth.account.utils import send_email_confirmation
						send_email_confirmation(request, user_obj)
						responsedict['success'] = True
				except Exception as e:
						responsedict['success'] = False
		
				return HttpResponse(json.dumps(responsedict), mimetype="application/json")
						

class UserAcknowledgementView(TemplateView):
        template_name = 'mixtape/user_acknowledgement.html'
		
class validateSignupForm(AjaxResponseMixin, JSONResponseMixin,View):       
    def post_ajax(self, request, *args, **kwargs):
        
            data = self.request._post
            responsedict = {}
            username_error = None
            cell_phone_error = None
            password_error = None
            email_error =None				
            
            try:
                try:
                    if username:
                		username_error = "This username already exists. Please choose another one"							
                except:
                    username_error = None
                try:
                        email = User.objects.filter(email=data['email'])
                        if email:
                                email_error = "This email already exists. Please choose another one"                            
                except:
                        email_error =None
                
                try:
                		cell_phone = UserProfile.objects.filter(cell_phone = data['cell_phone'])
                		if cell_phone:
                				cell_phone_error = "Sorry. This cell phone number is already associated with a 24/7Mixtapes account. Please try again."
                except:
                		cell_phone_error = None
                if data["password1"] != data["password2"]:
                		password_error = "You must type the same password each time."
                						
                responsedict['username_error'] = username_error
                responsedict['cell_phone_error'] = cell_phone_error
                responsedict['password_error'] = password_error
                responsedict['email_error'] = email_error
                							
                responsedict['success'] = True
            except:
            		#messages.info(self.request, 'Unable to send verification text to your given cell phone. Please try again')
            		responsedict['message_info'] = 'Unable to send verification text to your given cell phone. Please try again.'
            		responsedict['success'] = False
            
            return HttpResponse(json.dumps(responsedict), mimetype="application/json")
						
class ContactUsView(TemplateView):
        template_name = 'mixtape/contactus.html'
       
 
class AddSubscriptionView(AjaxResponseMixin, JSONResponseMixin, View):
    def post_ajax(self, request, *args, **kwargs):
            data = self.request._post
            responsedict = {}
            try:
                    if data['artist']:
                        artist=UserProfile.objects.get(id=data['artist'])
                        if data['action'] == 'Subscribe':
                            p, created =ArtistSubscription.objects.get_or_create(user=request.user.userprofile,artist = artist)
                            responsedict['subscribe'] = 'Unsubscribe'
                        else:
                            ArtistSubscription.objects.get(user=request.user.userprofile,artist = artist).delete()
                            responsedict['subscribe'] = 'Subscribe'
                    responsedict['success'] = True
            except Exception as e:
                    print e
                    responsedict['success'] = False
    
            return HttpResponse(json.dumps(responsedict), mimetype="application/json")      
       
  
class AddFavorite(AjaxResponseMixin, JSONResponseMixin, View):
        def post_ajax(self, request, *args, **kwargs):
                data = self.request._post
                responsedict = {}
                try:
                        if data['mixtape']:
                            if Mixtape.objects.filter(id=data['mixtape']).exists():
                                mts = Mixtape.objects.filter(id=data['mixtape'])
                                if mts:
                                    mt = mts[0]
                            else:
                                mt = None
                            if mt:
                                if data['favorite'] == 'Favorite':
                                    p, created =MixtapeFavorite.objects.get_or_create(mixtape=mt,user=request.user.userprofile)
                                    #favorite_obj = MixtapeFavorite(mixtape=mt,user=request.user.userprofile)
                                    #favorite_obj.save()
                                    responsedict['favorite'] = 'Unfavorite'
                                else:
                                    MixtapeFavorite.objects.get(mixtape=mt,user=request.user.userprofile).delete()
                                    responsedict['favorite'] = 'Favorite'
                        responsedict['success'] = True
                except Exception as e:
                        print e
                        responsedict['success'] = False
        
                return HttpResponse(json.dumps(responsedict), mimetype="application/json")
	
	
class AddStreamCount(AjaxResponseMixin, JSONResponseMixin, View):
        def post_ajax(self, request, *args, **kwargs):
                data = self.request._post
                responsedict = {}
                try:
			if data['mixtape']:
				if Mixtape.objects.filter(id=data['mixtape']).exists():
					mts = Mixtape.objects.filter(id=data['mixtape'])
				if mts:
					mt = mts[0]
				else:
					mt = None
				if mt:
					if mt.soundcloud_favoritings_count:
						mt.soundcloud_favoritings_count = mt.soundcloud_favoritings_count+1
					else:
						mt.soundcloud_favoritings_count = 1
					mt.save()
			responsedict['stream_count'] = mt.soundcloud_favoritings_count
			responsedict['success'] = True
                except Exception as e:
                        print e
                        responsedict['success'] = False
        
                return HttpResponse(json.dumps(responsedict), mimetype="application/json")
        

class AddContactUsView(AjaxResponseMixin, JSONResponseMixin, View):
        def post_ajax(self, request, *args, **kwargs):
                data = self.request._post
                responsedict = {}
                try:
                        if data['email']:
                                email_message = send_mail(data['topic'],data['message'],data['email'] ,
                                    [settings.DEFAULT_FROM_EMAIL], fail_silently=False) 
                                #email_message = send_mail(data['topic'], data['message'], settings.DEFAULT_FROM_EMAIL,
                                    #[settings.DEFAULT_FROM_EMAIL], fail_silently=False)                        
                        responsedict['success'] = True
                except Exception as e:
                        print e
                        responsedict['success'] = False
        
                return HttpResponse(json.dumps(responsedict), mimetype="application/json")
            
            
            
class AnalyticsTrackView(AjaxResponseMixin, JSONResponseMixin, View):
        def post_ajax(self, request, *args, **kwargs):
                data = self.request._post
                responsedict = {}
                try:
                        if data['analytics']:
                            if re.match('UA-\d{4,9}-\d{1,4}',data['analytics'].strip()) == None:
                                responsedict['success'] = False
                            else:
                                user = UserProfile.objects.get(user =request.user)
                                user.tracking_code  =  data['analytics']    
                                user.save()    
                                responsedict['success'] = True
                except Exception as e:
                        print e
                        responsedict['success'] = False
        
                return HttpResponse(json.dumps(responsedict), mimetype="application/json")            
            
  
class TermsView(TemplateView):
        template_name = 'mixtape/terms.html'
        
        
class DMCAView(TemplateView):
        template_name = 'mixtape/dmca.html'
        
class PrivacyView(TemplateView):
        template_name = 'mixtape/privacy.html'  
        
class AdvertiseView(TemplateView):
        template_name = 'mixtape/advertise.html'  
        


from django.contrib.auth.decorators import login_required
@login_required
def limit_download_sample(request):
    if request.is_ajax():
        response = captcha.submit(
            request.GET.get('abc'),
            request.GET.get('xys'),
            settings.RECAPTCHA_PRIVATE_KEY,
            request.META['REMOTE_ADDR'],)
        import datetime
        responsedict={}
        try:
            p = MixtapeDownloadLimit.objects.get(date=datetime.datetime.now().date(),user=request.user.username)
        except MixtapeDownloadLimit.DoesNotExist:
            MixtapeDownloadLimit.objects.filter(date__lt=datetime.datetime.now().date(),user=request.user.username).delete()
            p = MixtapeDownloadLimit.objects.create(date=datetime.datetime.now().date(),user=request.user.username)
        if p.count<UserProfile.objects.get(user__username=request.user.username).download_limit:
            if response.is_valid:
		p.count = p.count+1
                p.save()
                responsedict['success'] = True
                responsedict['count'] = request.user.userprofile.download_limit-p.count
                return HttpResponse(json.dumps(responsedict), mimetype="application/json")
            else:
                responsedict['success'] = False
                responsedict['count'] = UserProfile.objects.get(user__username=request.user.username).download_limit-p.count
                responsedict['captcha_response'] = 'Try again'
                return HttpResponse(json.dumps(responsedict), mimetype="application/json")
        else:
            responsedict['success'] = False
            responsedict['count'] = UserProfile.objects.get(user__username=request.user.username).download_limit-p.count
            return HttpResponse(json.dumps(responsedict), mimetype="application/json")
    else:
        return HttpResponse("Invalid")

#@login_required
def fp_details(request):
    if request.is_ajax():
	    responsedict={
		    'FILEPICKER_API_KEY': settings.FILEPICKER_API_KEY,
		    'FILEPICKER_UPLOAD_POLICY': getpolicy('upload'),
		    'FILEPICKER_UPLOAD_SIGNATURE': getsignature('upload'),
		    'FILEPICKER_READ_POLICY': getpolicy('read'),
		    'FILEPICKER_READ_SIGNATURE': getsignature('read'),
		    'FILEPICKER_DELETE_POLICY': getpolicy('delete'),
		    'FILEPICKER_DELETE_SIGNATURE': getsignature('delete'),
	            'FILEPICKER_DOWNLOAD_POLICY' : getpolicy('download'),
	            'FILEPICKER_DOWNLOAD_SIGNATURE' : getsignature('download'),
		}
	    return HttpResponse(json.dumps(responsedict), mimetype="application/json")
	    

from django.contrib.auth.decorators import login_required
@login_required
def limit_download(request):
    if request.is_ajax():
        import datetime
        responsedict={}
        try:
            mixtape_download = MixtapeDownloadLimit.objects.get(date=datetime.datetime.now().date(),user=request.user.username)
        except MixtapeDownloadLimit.DoesNotExist:
            MixtapeDownloadLimit.objects.filter(date__lt=datetime.datetime.now().date(),user=request.user.username).delete()
            mixtape_download = MixtapeDownloadLimit.objects.create(date=datetime.datetime.now().date(),user=request.user.username)
        if mixtape_download.count>=UserProfile.objects.get(user__username=request.user.username).download_limit:
            responsedict['success'] = False
            responsedict['count'] = UserProfile.objects.get(user__username=request.user.username).download_limit-mixtape_download.count
            return HttpResponse(json.dumps(responsedict), mimetype="application/json")
        else:
            mixtape_download.count = mixtape_download.count+1
            mixtape_download.save()
            responsedict['success'] = True
            responsedict['count'] = request.user.userprofile.download_limit-mixtape_download.count
            return HttpResponse(json.dumps(responsedict), mimetype="application/json")
    else:
        return HttpResponse("Invalid")

   
def download_sampleTrack(request,id):
    obj = Mixtape.objects.get(id=id)
    for i in obj.tracks.all():
        if i.order == 3:
            url = i.url
            break
    import urllib
    currentsite = get_current_site(request)
    url=currentsite.domain+url
    content = urllib.urlretrieve(url)

    response= HttpResponse(content,mimetype="application/mp3")
    response['Content-Disposition'] = 'attachment; filename=' + str('247mixtapes.mp3') 
    return response
    
    
class SearchView(ListView):
    model = Mixtape
    template_name = 'mixtape/search.html'
    
    def get_queryset(self):
        query = self.request.GET.get('name','')
        qs=[]
        if query:
            qs = Mixtape.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(primaryArtist__username__icontains=query),approved=True,releaseDatetime__lt=datetime.now(pytz.utc)).order_by('updated')
        return qs


#Views created for Genres

class RapMixtapView(ListView):
    model = Mixtape
    template_name = 'mixtape/rap_mixtapes.html'

    def get_context_data(self, **kwargs):
        context = super(RapMixtapView, self).get_context_data(**kwargs)
        genre = Genre.objects.get(name='Rap')
        if genre != '':
            object_list = Mixtape.objects.filter(primaryGenre = genre,approved=True).order_by('-id')[:40]
        else:

            object_list = Mixtape.objects.filter(approved=True).order_by('-id')[:40]
        context['object_list'] = object_list
        history = object_list
        paginator = Paginator(history, 40) # Show 25 contacts per page
        page = self.request.GET.get('page')
        try:
            history = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            history = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            history = paginator.page(paginator.num_pages)

        context['tap_list'] = history
        return context

class BlendsMixtapView(ListView):
    model = Mixtape
    template_name = 'mixtape/blend_mixtapes.html'

    def get_context_data(self, **kwargs):
        context = super(BlendsMixtapView, self).get_context_data(**kwargs)
        genre = Genre.objects.get(name='Blends')
        if genre != '':
            object_list = Mixtape.objects.filter(primaryGenre = genre,approved=True).order_by('-id')[:40]
        else:
            object_list = Mixtape.objects.filter(approved=True).order_by('-id')[:40]
        context['object_list'] = object_list
        history = object_list
        paginator = Paginator(history, 40) # Show 25 contacts per page
        page = self.request.GET.get('page')
        try:
            history = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            history = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            history = paginator.page(paginator.num_pages)

        context['tap_list'] = history
        return context

class ReggaeMixtapView(ListView):
    model = Mixtape
    template_name = 'mixtape/reggae_mixtapes.html'

    def get_context_data(self, **kwargs):
        context = super(ReggaeMixtapView, self).get_context_data(**kwargs)
        genre = Genre.objects.get(name='Reggae')
        if genre != '':
            object_list = Mixtape.objects.filter(primaryGenre = genre,approved=True).order_by('-id')[:40]
        else:
            object_list = Mixtape.objects.filter(approved=True).order_by('-id')[:40]
        context['object_list'] = object_list
        history = object_list
        paginator = Paginator(history, 40) # Show 25 contacts per page
        page = self.request.GET.get('page')
        try:
            history = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            history = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            history = paginator.page(paginator.num_pages)

        context['tap_list'] = history
        return context

class EastCoastMixtapView(ListView):
    model = Mixtape
    template_name = 'mixtape/eastcoast_mixtapes.html'

    def get_context_data(self, **kwargs):
        context = super(EastCoastMixtapView, self).get_context_data(**kwargs)
        genre = Genre.objects.get(name='East Coast')
        if genre != '':
            object_list = Mixtape.objects.filter(primaryGenre = genre,approved=True).order_by('-id')[:40]
        else:
            object_list = Mixtape.objects.filter(approved=True).order_by('-id')[:40]
        context['object_list'] = object_list
        history = object_list
        paginator = Paginator(history, 40) # Show 25 contacts per page
        page = self.request.GET.get('page')
        try:
            history = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            history = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            history = paginator.page(paginator.num_pages)

        context['tap_list'] = history
        return context

class DirtySouthMixtapView(ListView):
    model = Mixtape
    template_name = 'mixtape/dirtysouth_mixtapes.html'

    def get_context_data(self, **kwargs):
        context = super(DirtySouthMixtapView, self).get_context_data(**kwargs)
        genre = Genre.objects.get(name='Dirty South')
        if genre != '':
            object_list = Mixtape.objects.filter(primaryGenre = genre,approved=True).order_by('-id')[:40]
        else:
            object_list = Mixtape.objects.filter(approved=True).order_by('-id')[:40]
        context['object_list'] = object_list
        history = object_list
        paginator = Paginator(history, 40) # Show 25 contacts per page
        page = self.request.GET.get('page')
        try:
            history = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            history = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            history = paginator.page(paginator.num_pages)

        context['tap_list'] = history
        return context

class RBMixtapView(ListView):
    model = Mixtape
    template_name = 'mixtape/rnb_mixtapes.html'

    def get_context_data(self, **kwargs):
        context = super(RBMixtapView, self).get_context_data(**kwargs)
        genre = Genre.objects.get(name='R&B')
        if genre != '':
            object_list = Mixtape.objects.filter(primaryGenre = genre,approved=True).order_by('-id')[:40]
        else:
            object_list = Mixtape.objects.filter(approved=True).order_by('-id')[:40]
        context['object_list'] = object_list
        history = object_list
        paginator = Paginator(history, 40) # Show 25 contacts per page
        page = self.request.GET.get('page')
        try:
            history = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            history = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            history = paginator.page(paginator.num_pages)

        context['tap_list'] = history
        return context

class ChoppedMixtapView(ListView):
    model = Mixtape
    template_name = 'mixtape/chopped_mixtapes.html'

    def get_context_data(self, **kwargs):
        context = super(ChoppedMixtapView, self).get_context_data(**kwargs)
        genre = Genre.objects.get(name='Chopped & Screwed')
        if genre != '':
            object_list = Mixtape.objects.filter(primaryGenre = genre,approved=True).order_by('-id')[:40]
        else:
            object_list = Mixtape.objects.filter(approved=True).order_by('-id')[:40]
        context['object_list'] = object_list
        history = object_list
        paginator = Paginator(history, 40) # Show 25 contacts per page
        page = self.request.GET.get('page')
        try:
            history = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            history = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            history = paginator.page(paginator.num_pages)

        context['tap_list'] = history
        return context

class InstrumentalsMixtapView(ListView):
    model = Mixtape
    template_name = 'mixtape/instrumental_mixtapes.html'

    def get_context_data(self, **kwargs):
        context = super(InstrumentalsMixtapView, self).get_context_data(**kwargs)
        genre = Genre.objects.get(name='Instrumentals')
        if genre != '':
            object_list = Mixtape.objects.filter(primaryGenre = genre,approved=True).order_by('-id')[:40]
        else:
            object_list = Mixtape.objects.filter(approved=True).order_by('-id')[:40]
        context['object_list'] = object_list
        history = object_list
        paginator = Paginator(history, 40) # Show 25 contacts per page
        page = self.request.GET.get('page')
        try:
            history = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            history = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            history = paginator.page(paginator.num_pages)

        context['tap_list'] = history
        return context
         

def captcha_download(request):
    if request.is_ajax():
        data = {
            'challenge': request.POST.get('abc'),
            'response': request.POST.get('xys'),
            'key': settings.RECAPTCHA_PRIVATE_KEY,
            'addr': request.META['REMOTE_ADDR'],
        }
        print data
        response = captcha.submit(
            request.POST.get('abc'),
            request.POST.get('xys'),
            settings.RECAPTCHA_PRIVATE_KEY,
            request.META['REMOTE_ADDR'],)
        responsedict={}
        if response.is_valid:
            responsedict['success'] = True
        else:
            responsedict['success'] = False
            responsedict['captcha_response'] = 'Try again'
        return HttpResponse(json.dumps(responsedict), mimetype="application/json")
    else:
        return HttpResponse("Invalid")

#section for uncomplete phone verification
class PhoneVerifyView(AjaxResponseMixin, JSONResponseMixin, LoginRequiredMixin, View):

		def post_ajax(self, request, *args, **kwargs):
				data = self.request._post
				responsedict = {}
				try:
						user_obj = User.objects.create_user(username=data['data[username][]'], email=data['data[email][]'])
						user_obj.set_password(data['data[password1][]'])
						user_obj.is_active = True
						user_obj.save()

						userprofile_obj = user_obj.userprofile
						userprofile_obj.cell_phone = data['data[cell_phone][]']
                                                userprofile_obj.phon_verified = False
                                                userprofile_obj.verify_code = data['code']
						userprofile_obj.save()

						#verify_obj = TwilioVerification(user=user_obj, to=data['data[cell_phone][]'],from_= settings.TWILIO_NUMBER,
												        #body=data['message_body'],sid=data['message'],
												        #content_type_id=user_obj.userprofile.get_content_type_id(),
												        #object_id=user_obj.userprofile.id, verified=True)
						#verify_obj.save
						new_user = authenticate(username=data['data[username][]'], password=data['data[password1][]'])
						login(self.request, new_user)
						messages.success(self.request,'Your account has been created but not yet verified. Please verify soon.')
						if data['data[email][]']:
								email_message = send_mail('Welcome to 24/7Mixtapes', 'Your account has now been created and verified. Welcome to 247Mixtapes.com!.', settings.DEFAULT_FROM_EMAIL,
									[data['data[email][]']], fail_silently=False)
						responsedict['success'] = True
				except Exception as e:
						responsedict['success'] = False

				return HttpResponse(json.dumps(responsedict), mimetype="application/json")

class PhoneReVerifyView(AjaxResponseMixin, JSONResponseMixin, LoginRequiredMixin, View):

		def post_ajax(self, request, *args, **kwargs):
				data = self.request._post
				responsedict = {}

				try:
						user_obj = User.objects.get(id=data['id'])
						user_obj.is_active = True
						user_obj.save()

						userprofile_obj = user_obj.userprofile
                                                userprofile_obj.phon_verified = True
                                                userprofile_obj.verify_code = data['code']
						userprofile_obj.save()

						#verify_obj = TwilioVerification(user=user_obj, to=data['data[cell_phone][]'],from_= settings.TWILIO_NUMBER,
												        #body=data['message_body'],sid=data['message'],
												        #content_type_id=user_obj.userprofile.get_content_type_id(),
												        #object_id=user_obj.userprofile.id, verified=True)
						#verify_obj.save
#						new_user = authenticate(username=data['data[username][]'], password=data['data[password1][]'])
#						login(self.request, new_user)
#						messages.success(self.request,'Your account has now been created.But not yet verified.Please verify soon.')
#						if data['data[email][]']:
#								email_message = send_mail('Welcome to 247mixtapes', 'Your account has now been created and verified. Welcome to 247Mixtapes.com!.', settings.DEFAULT_FROM_EMAIL,
#									[data['data[email][]']], fail_silently=False)
						responsedict['success'] = True
				except Exception as e:
						responsedict['success'] = False

				return HttpResponse(json.dumps(responsedict), mimetype="application/json")

class TestView(TemplateView):
        template_name = 'test.html'

#customized email view(in allauth)
class MyEmailView(LoginRequiredMixin, EmailView):
        template_name = "account/email.html"

        def get_context_data(self, **kwargs):
                ret = super(MyEmailView, self).get_context_data(**kwargs)
                ret['email_addresses_verified'] = self.request.user.emailaddress_set.filter(verified=True)
                ret['email_addresses_nonverified'] = self.request.user.emailaddress_set.filter(verified=False)
                return ret

#from django.db.models import Q
#results = BlogPost.objects.filter(Q(title__icontains=your_search_query) | Q(intro__icontains=your_search_query) | Q(content__icontains=your_search_query)).order_by('pub_date')
