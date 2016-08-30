from django.shortcuts import get_object_or_404, render
from braces import views
from django.views.generic import *
from django.http import HttpResponseRedirect,HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from payments.models import *
from addon.models import *
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.safestring import mark_safe
from django.conf import settings
from cgi import escape

from braces.views import JSONResponseMixin, AjaxResponseMixin, CsrfExemptMixin

from mixtape.models import *
from userprofile.models import *
from Mixtapes.forms import UserProfileUpdateForm
from django.views.generic import DetailView

from Mixtapes.utils.access import LoginRequiredMixin


class MyProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'my-account/my-profile.html'
    
class UserProfileUpdateView(LoginRequiredMixin, UpdateView,DetailView):
    model = UserProfile
    template_name = 'my-account/my_profile_update.html'
    
    form_class = UserProfileUpdateForm
    
    def get_form_kwargs(self):
        kwargs = super(UserProfileUpdateView, self).get_form_kwargs()
        kwargs.update({'place_user': self.request.user})
        return kwargs
    
    def form_invalid(self, form):
        context = self.get_context_data()
        context['form'] = form
        self.template_name = 'my-account/form_valid.html'
        return render(self.request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super(UserProfileUpdateView, self).get_context_data(**kwargs)
        context['form'] = UserProfileUpdateForm(instance=UserProfile.objects.get(user=self.request.user))
        return context


    def get_object(self):
        return get_object_or_404(UserProfile, user=self.request.user)

    def form_valid(self, form):

        '''
        Override to include the fields for saving of model.
        These fields were manually excluded in the form to trigger this pathway
        instead of form_valid()
        '''
        if UserProfile.objects.filter(username=self.request.user.username).exists():
            obj = UserProfile.objects.get(username=self.request.user.username)
            obj.aboutme = form.cleaned_data['aboutme']
            obj.video = form.cleaned_data['video']
            #obj.homepage = form.cleaned_data['homepage']
            obj.facebook = form.cleaned_data['facebook']
            obj.twitter = form.cleaned_data['twitter']
            obj.google = form.cleaned_data['google']
            obj.youtube = form.cleaned_data['youtube']
            obj.save()
        else:
            obj = form.save(commit=False)
            self.object = obj
            obj.user = self.request.user
            obj.slug = slugify(self.request.user.username)
            obj.save()
        messages.info(self.request, 'userprofile updated')
        
        self.template_name = 'my-account/form_valid.html'
        context = self.get_context_data()
        context['success'] = 'success'
        return render(self.request, self.template_name, context)#return HttpResponse('success')

    def get_success_url(self):
            return HttpResponseRedirect('/my-profile')


class MyMixtapesView(LoginRequiredMixin,ListView):
    model = Mixtape
    template_name = 'my-account/my-mixtapes.html'
    
    def get_context_data(self, **kwargs):
    	context = super(MyMixtapesView, self).get_context_data(**kwargs)
    	context['username'] = self.request.user.username
    	waitingapproval = Mixtape.objects.select_related().filter(created_by=self.request.user, approved=False).order_by('-id')
        history = Mixtape.objects.select_related().filter(created_by=self.request.user, approved=True).order_by('-id')
                
        
        paginator = Paginator(history, 40) # Show 25 contacts per page
        paginator_waiting = Paginator(waitingapproval, 40) # Show 25 contacts per page
    
        page = self.request.GET.get('page')
        try:
            history = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            history = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            history = paginator.page(paginator.num_pages)
            
        try:
            waitingapproval = paginator_waiting.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            waitingapproval = paginator_waiting.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            waitingapproval = paginator_waiting.page(paginator_waiting.num_pages)
        
        
        
        context['object_list'] = history
        context['waitingapproval'] = waitingapproval
    	return context
    

    def get_queryset(self):
        return Mixtape.objects.filter(created_by=self.request.user)
    


class MyAddonsView(TemplateView):
    template_name = 'my-account/my-addons.html'

    def get_context_data(self, **kwargs):
        context = super(MyAddonsView, self).get_context_data(**kwargs)
        cats = AddonCategory.objects.all()
        addons = AddonType.objects.all()

        addon_categories = [{'name':c.name, 'addons':filter(lambda x: x.category == c, addons)} for c in cats]
        context['addon_categories'] = addon_categories

        return context        

class ChangeCardView(views.JSONResponseMixin, views.AjaxResponseMixin, View):
    def get(self, request, *args, **kwargs):
        return redirect(reverse('my-account:payments'))

    def post_ajax(self, request, *args, **kwargs):
        #print request.POST

        data = {}

        try:
            if request.user.customer:
                print 'Customer for %s found!' % request.user.username
                try:
                    print '\t--> attempting to update card.'
                    update = request.user.customer.update_card(token=request.POST['stripeToken'])
                    data['success'] = True
                    data['plan'] = request.session.get('plan')
                    if not data['plan'] == None:
                        data['flag'] = True
                    else:
                        data['flag'] = False

                except Exception as e:
                    data['success'] = False
                    data['exception'] = '%s' % e

        except:
            print 'No customer for %s found!' % request.user.username
            try:
                print '\t--> attempting to create user.'
                customer = Customer.create(user=request.user, card=request.POST['stripeToken'])
                data['success'] = True
                data['plan'] = request.COOKIES['plan']
                if not data['plan'] == None:
                    data['flag'] = True
                else:
                    data['flag'] = False
            except Exception as e:
                data['success'] = False
                data['exception'] = '%s' % e

        return self.render_json_response(data)

    def delete_ajax(self, request, *args, **kwargs):

        data = {}

        try:
            print 'Trying to delete!'
            customer = request.user.customer
            stripe_customer = customer.stripe_customer
            card = stripe_customer.cards['data'][0]['id']

            print '\t--> deleting from stripe API'
            #Delete via API on stripe
            stripe_customer.cards.retrieve(card).delete()

            print '\t--> syncing locally'
            #Also clear this on our model
            customer.sync()

            data['success'] = True
            data['message'] = 'Card successfully deleted'

        except Exception as e:
            data['success'] = False
            data['message'] = '%s' % e

        return self.render_json_response(data)



class PaymentsView(LoginRequiredMixin,TemplateView):
    template_name = "my-account/my-payments.html"

    def get_context_data(self, **kwargs):
        context = super(PaymentsView, self).get_context_data(**kwargs)
        context['plans'] = [
            {'name':settings.PAYMENTS_PLANS[k]['name'], 'price':'$%s/%s' % (v['price'], v['interval'])} for k, v in settings.PAYMENTS_PLANS.iteritems()
            ] 
        try:
            s=self.request.user.id,self.request.user.customer.id
        except Exception,e:
            print e
        history = AddonCharge.objects.filter(updated_by=self.request.user.id)
        
        paginator = Paginator(history, 25) # Show 25 contacts per page
    
        page = self.request.GET.get('page')
        try:
            history = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            history = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            history = paginator.page(paginator.num_pages)
        context['history'] =history
        #context['plans_history'] = Charge.objects.filter(customer=self.request.user.customer, description__contains="|Plan")
        return context

class AJAXCancelPlanView(views.JSONResponseMixin, views.AjaxResponseMixin, View):
    def post_ajax(self, request, *args, **kwargs):
        data = {}
        try:            
            request.user.customer.cancel()
            data['success'] = True

        except:
            data['success'] = False

        return self.render_json_response(data)

class AJAXUpgradePlanView(views.JSONResponseMixin, views.AjaxResponseMixin, View):
    def post_ajax(self, request, *args, **kwargs):
        data = {}
        plan = request.POST['plan']

        if plan == 'monthly' and request.user.customer.current_subscription.plan == 'yearly':
            data['success'] = False
            data['message'] = 'Downgrading from existing premium yearly to monthly membership is not permitted.'
            return self.render_json_response(data)

        else:
            try:        
                request.user.customer.subscribe(plan)
                data['success'] = True
            except Exception as e:
                data['success'] = False
                data['message'] = '%s' % e
            return self.render_json_response(data)      
        
        
#class MixtapeDetailView(ListView):
	#model = Mixtape
	#template_name = 'my-account/mixtape_detail_released.html'
	    
	#def get_context_data(self, **kwargs):
		#mixtape_id = self.request.GET['mixtapeid']
		#context = super(MixtapeDetailView, self).get_context_data(**kwargs)
		#context['username'] = self.request.user.username
		#mixtape_obj = Mixtape.objects.get(id=mixtape_id)
		#context['object'] = mixtape_obj
		#return context
			
	#def get_queryset(self):
		#mixtape_id = self.kwargs['mixtapeid']
		#return Mixtape.objects.filter(created_by=self.request.user)
				
class MixtapeDetailView(DetailView):
    model = Mixtape
    template_name = 'my-account/mixtape_detail_released.html'
    released_template_name = 'my-account/mixtape_detail_released.html'
    countdown_template_name = 'my-account/mixtape_countdown.html'
    coming_soon_template_name = 'my-account/mixtape_coming_soon.html'
    def get_context_data(self, **kwargs):
            context = super(MixtapeDetailView, self).get_context_data(**kwargs)
#             info = {
#             		'primaryArtist__username':self.kwargs['artist'],
#             		'slug':self.kwargs['slug'],
#             		'created_by':UserProfile.objects.get(user__username=self.kwargs['uploader']).user
#             	}
            mts = Mixtape.objects.filter(id=self.kwargs['id'])
	    img=""
	    images=""
            seton = settings.MEDIA_URL
            context['set'] = seton
	    googleads = GoogleAdsBlock.objects.all()
	    if googleads:
		context['ads'] = googleads[0]

            if mts:
            	mt = mts[0]
            else:
            	mt = None
            context['mt'] = mt
	    
            if mt:
                images = mt.images.all()
                if images:
                    img = images[0]
                    context['image'] = img.get_thumbnail()

	    context['trackslist'] = __builtins__['list'](mt.tracks.all())
	    context['trackslist'].insert((2 if len(context['trackslist'])>2 else len(context['trackslist'])), {'order': 3, 'url': 'http://static.247mixtapes.com/upload/audiofiles/247Mixtapes.mp3', 'filename': '247mixtapes-drop'})
	    context['total'] = len(context['trackslist'])
            context['object'] = mt
            mixtapesview = MixtapePageView.objects.filter(mixtape_id = self.kwargs['id'])
            try:
                favorite = MixtapeFavorite.objects.get(mixtape=mt,user=self.request.user.userprofile)
            except:
                favorite = []
            context['favorite'] = favorite
            context['mixtapeviews'] = len(mixtapesview)
            from datetime import datetime
            fadd = AddonType.objects.get(name__iexact='Basic Mixtape Page Countdown',duration='7')
            alladdons = AddonCharge.objects.filter(
                addon=fadd,
                end_datetime__gt=datetime.now(pytz.utc),
                mixtape__approved=True
                ).prefetch_related()
            fadd = AddonType.objects.get(name__iexact='Custom Skin On Mixtape Page')
            allskins = AddonCharge.objects.filter(
                addon=fadd,
                mixtape__approved=True
                ).prefetch_related()
            #print len(featured)
            
            if allskins:
                context['custom_skin'] =False
                #Get the related mixtape objects
                #alladdons = [f.mixtape for f in alladdons]
                for i in allskins:
                    if mt.id == i.object_id:
                        context['custom_skin']= True
                        break
                    
            if alladdons:
                context['countdown'] =False
                #Get the related mixtape objects
                #alladdons = [f.mixtape for f in alladdons]
                for i in alladdons:
                    if mt.id == i.object_id:
                        context['countdown']= True
                        break
                    
            fadd = AddonType.objects.get(name__iexact='Sponsored Mixtape',duration='7')
            sponsered = AddonCharge.objects.filter(
                addon=fadd,
                end_datetime__gt=datetime.now(pytz.utc),
                mixtape__approved=True
                ).prefetch_related()
            
            #print len(featured)
            if sponsered:
                context['sponsered'] =False
                #Get the related mixtape objects
                #alladdons = [f.mixtape for f in alladdons]
                for i in sponsered:
                    if mt.id == i.object_id:
                        context['sponsered']= True
                        break
                    
                          
            fadd = AddonType.objects.get(name__iexact='Featured Mixtape')
            featured = AddonCharge.objects.filter(
                addon=fadd,
                #end_datetime__gt=datetime.now(pytz.utc),
                mixtape__approved=True
                ).prefetch_related()
            
            #print len(featured)
            if featured:
                context['featured'] =False
                #Get the related mixtape objects
                #alladdons = [f.mixtape for f in alladdons]
                for i in featured:
                    if mt.id == i.object_id:
                        context['featured']= True
                        break
                  
            import datetime
            try:
                limit =self.request.user.userprofile.download_limit
            except:
                limit =5
            
            try:
                d_count = limit-MixtapeDownloadLimit.objects.get(date=datetime.datetime.now().date(),user=self.request.user.username).count
            except Exception,e:
                d_count = limit
            context['count'] = d_count
            return context
         
    def dispatch(self, request, *args, **kwargs):
        #import pdb;pdb.set_trace()
 
        if UserProfile.objects.filter(user__username=self.request.user.username).exists():
            cb = UserProfile.objects.get(user__username=self.request.user.username).user
        else:
            cb = None
#         info = {
#             'primaryArtist__username':self.kwargs['artist'],
#             'slug':self.kwargs['slug'],
#             'created_by':cb
#         }
 
        if Mixtape.objects.filter(id=self.kwargs['id'],approved=True).exists():
            mts = Mixtape.objects.filter(id=self.kwargs['id'])
            if mts:
                mt = mts[0]
        else:
            mt = None
        if mt:
            page_view_obj = MixtapePageView(mixtape=mt)
            page_view_obj.save()
            if mt.approved:
                return super(MixtapeDetailView, self).dispatch(request, *args, **kwargs)
            else:
                messages.error(self.request, 'Not Yet Available: \"%s\" by %s' % (self.request.user.username, self.request.user.username))
                return redirect('/my-profile')
        else:
            messages.error(self.request, 'Not Found: \"%s\" by %s' % (self.request.user.username, self.request.user.username))
            if UserProfile.objects.filter(user__username=self.request.user.username).exists():
                return redirect('/my-profile')
            elif UserProfile.objects.filter(user__username=self.request.user.username).exists():
                return redirect('/my-profile')
            else:
                return redirect('/')

    def get_object(self):
# 		info = {
# 			'primaryArtist__slug':self.kwargs['artist'],
# 			'slug':self.kwargs['slug'],
# 			'created_by':UserProfile.objects.get(user__username=self.request.user.username).user
# 		}
		mts = Mixtape.objects.filter(id=self.kwargs['id'])
		if mts:
			mt = mts[0]
		else:
			mt = None
				
		if mt:
			if mt.isReleased:
				setattr(self, 'template_name', self.released_template_name)
				#If not yet released...
			else:
				#Show the mixtape to the author...
				if mt.created_by == self.request.user or self.request.user.has_perm('can_preview', mt):
                                    
					messages.info(self.request, mark_safe('''You are seeing this alert because you submitted a future release mixtape without purchasing a Pre-Release Upgrade. If you want to remove the red error message above and unlock features like having a countdown timer, social share buttons mixtape cover previews, and a comments box, then purchase a Pre-Release Upgrade <a href="/%s/addons/">here</a>''' %  escape(self.kwargs['id'])))
					setattr(self, 'template_name', self.released_template_name)
		
					#If not the author...
				else:
					setattr(self, 'template_name', self.coming_soon_template_name)
		
						
		
				return mt

class FavoriteMixtapView(ListView):
        model = MixtapeFavorite
        template_name = 'mixtape/my_favorites.html'
                
        def get_context_data(self, **kwargs):
                context = super(FavoriteMixtapView, self).get_context_data(**kwargs)
                context['object_list'] = MixtapeFavorite.objects.filter(user=self.request.user.userprofile).order_by('-mixtape').distinct('mixtape')
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
                return context
    
class MySubscriptionsView(LoginRequiredMixin, ListView):
    model = ArtistSubscription
    template_name = 'payments/my_subscriptions.html'
    
    
    def get_context_data(self, **kwargs):
        context = super(MySubscriptionsView, self).get_context_data(**kwargs)
        try:
            history = ArtistSubscription.objects.filter(user=self.request.user.userprofile)
        except:
            history = ''
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


class MyMembershipView(LoginRequiredMixin, TemplateView):
        template_name = 'payments/my_membership.html'

        
        
class PremiumMemberView( TemplateView):
        template_name = 'payments/premium_member.html'        
        
class PremiumPublisherView( TemplateView):
        template_name = 'payments/premium_publisher.html'
        
class PremiumView( TemplateView):
        template_name = 'payments/premium.html'        
		
class SubscribeEndpointView(LoginRequiredMixin, JSONResponseMixin, AjaxResponseMixin, View):
        def post_ajax(self, request, *args, **kwargs):
            responsedict = {}
            try:
                data = json.loads(self.request.body)
                subtype = data['type']
                cust = request.user.customer
                if subtype == 'publisher-cancel':
                    cust.publisher_cancel()
	        elif subtype == 'member-cancel':
		    cust.member_cancel()
		elif subtype.startswith('premium'):
		    if cust.has_active_publisher_subscription() == False:
			if cust.card_last_4:
			    PAYMENTS_PLANS = settings.PAYMENTS_PLANS[subtype]
			    s=cust.subscribe(subtype)
			    cu = cust
			    PAYMENTS_PLANS = settings.PAYMENTS_PLANS[subtype]
			    try:
				char = cu.charge(amount=Decimal(PAYMENTS_PLANS['price']), description=PAYMENTS_PLANS['name']+"|Plan")
			    except Exception,e:
				print e
			    userobj = self.request.user
			    edt = None
			    #ac = AddonCharge(
			        #end_datetime = edt,
			        #charge = char,
			        #addon = None,
			        #content_type_id=None,
			        #object_id=None,
			        #updated_by=userobj,
			        #created_by=userobj
			        #)
			    #ac.save()
			    if subtype in ['premium-publisher-monthly','premium-publisher-yearly']:
				objuser = UserProfile.objects.get(username=self.request.user.username)
				objuser.premium_publisher = True
				objuser.save()
		        else:
			    messages.error(self.request, 'Please update card on file before proceeding!')
			    return redirect(reverse('update_card'))
		    else:
			messages.info(request, 'You cannot subscribe to more than one premium plan at the same time! Wait until your current subscription is over.')
			return reverse('my_subscriptions')
		else:
		    if cust.has_active_member_subscription() == False:
			if cust.card_last_4:
			    PAYMENTS_PLANS = settings.PAYMENTS_PLANS[subtype]
			    s=cust.subscribe(subtype)
			    cu = cust
			    PAYMENTS_PLANS = settings.PAYMENTS_PLANS[subtype]
			    try:
				char = cu.charge(amount=Decimal(PAYMENTS_PLANS['price']), description=PAYMENTS_PLANS['name']+"|Plan")
			    except Exception,e:
				print e
			    userobj = self.request.user
			    edt = None
			    ac = AddonCharge(
			        end_datetime = edt,
			        charge = char,
			        addon = None,
			        content_type_id=None,
			        object_id=None,
			        updated_by=userobj,
			        created_by=userobj
			        )
			    ac.save()
			    if subtype in ['premium-publisher-monthly','premium-publisher-yearly']:
				objuser = UserProfile.objects.get(username=self.request.user.username)
				objuser.premium_publisher = True
				objuser.save()
			else:
			    messages.error(self.request, 'Please update card on file before proceeding!')
			    return redirect(reverse('update_card'))
		    else:
			messages.info(request, 'You cannot subscribe to more than one premium plan at the same time! Wait until your current subscription is over.')
			return reverse('my_subscriptions')		    
                responsedict['messges'] = str(messages)
                responsedict['success'] = True
            
            except Exception,e:
                print e
            	responsedict['success'] = False

            return HttpResponse(json.dumps(responsedict), mimetype="application/json")


