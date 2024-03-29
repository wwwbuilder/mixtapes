from django.core.cache import cache
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.db import models
from django.db.models.signals import *
from django.utils.translation import ugettext as _
from django.utils.text import slugify

from _base.models import *
from inkblob.models import InkBlob
from inkblob.utils import *
from django.core.urlresolvers import reverse

from embed_video.fields import EmbedVideoField

class UserProfile(BaseClass):
    #https://docs.djangoproject.com/en/dev/ref/contrib/auth/#django.contrib.auth.models.User
    #https://docs.djangoproject.com/en/1.5/topics/auth/customizing/#extending-django-s-default-user

    user = models.OneToOneField(User, blank=True, null=True)
    
    images = generic.GenericRelation('_misc.Image')
    username = models.CharField(max_length=150, unique=True)
    official = models.BooleanField(default=False)
    premium = models.BooleanField(default=False)
    
    country = models.ForeignKey('locality.Country', blank=True, null=True)
    territory = models.ForeignKey('locality.Territory', blank=True, null=True)
    
    #count down from 5 per day
    download_limit = models.PositiveIntegerField(default=5, blank=True, null=True)
    
    homepage = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    google = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)
    video = EmbedVideoField(blank=True, null=True)
    pinterest = models.URLField(blank=True, null=True)
    soundcloud = models.URLField(blank=True, null=True)
    
    genres = models.ManyToManyField('mixtape.Genre', blank=True, null=True)
    aboutme = models.TextField(blank=True, null=True)
    
    active = models.BooleanField(default=True)
    cell_phone = models.CharField(max_length=25, blank=True, null=True,unique=True)
    views = models.IntegerField(default=0)
    premium_publisher = models.BooleanField(default=False)
    tracking_code = models.CharField(max_length=50, blank=True, null=True)
    phon_verified = models.BooleanField(default=False)
    verify_code = models.CharField(max_length=50, blank=True, null=True)

    def __unicode__(self):
        return '%s' % (self.username)
	
		
    #newchange
    @property
    def profile_image(self):
        upi = self.images.order_by('-updated')
        if upi:
                up = upi[0]
                #url = ''cache.get('profile_image_%s' % (up.pk))
                #if not url:
                        #url = '%s/convert?w=300&policy=%s&signature=%s' % (up.cdn_url, getpolicy('read'), getsignature('read'))
                        #cache.set('profile_image_%s' % up.pk, url, 60*60*24)
                        #return url
                #return url
                return up.default_url
        else:
                return 'https://placehold.it/250x250&text=No+Profile'   
			
    def get_artist_url(self):
        slug = slugify(self.user.username)
        print reverse('UserProfileImageView', kwargs={'slug':slug})
        return reverse('userprofileimage', kwargs={'slug':slug})	
    
    def get_url(self):
        slug = slugify(self.user.username)
        return "/user/%s" % slug

    def user_profile_image(self):
		upi = self.images.order_by('-updated')
		if upi:
			up = upi[0]
			#url = cache.get('%s_thumbnail_%s_%sx%s' % (up.__class__.__name__, self.pk, 250, 250))
			#if not url:
				#url = '%s/convert?w=250&h=250&fit=crop&policy=%s&signature=%s&format=jpg' % (up.cdn_url, getpolicy('read'), getsignature('read'))
				#cache.set('%s_thumbnail_%s_%sx%s' % (up.__class__.__name__, self.pk, 250, 250), url, 60*60*24)
			#return url
			return up.default_url
		else:
			return 'https://placehold.it/250x250&text=No+Profile'

    def small_profile_image(self):
        upi = self.images.order_by('-updated')
        if upi:
            up = upi[0]
            #url = cache.get('%s_thumbnail_%s_%sx%s' % (up.__class__.__name__, self.pk, 75, 75))
            #if not url:
                #url = '%s/convert?w=75&h=75&fit=crop&policy=%s&signature=%s&format=jpg' % (up.cdn_url, getpolicy('read'), getsignature('read'))
                #cache.set('%s_thumbnail_%s_%sx%s' % (up.__class__.__name__, self.pk, 75, 75), url, 60*60*24)
                #return url
            return up.default_url
        else:
             return 'https://placehold.it/75x75&text=No+Profile'

    def set_profile_image(self,imageid):
        if imageid:
            image = self.images.get(pk=imageid)
        else:
            image = self.images.latest('id')
        if image:
            image_url = image.get_image()
            return image_url


    

    # @property
    # def active_sixtydays(self):
    #     #Checks whether user has been active in the past 60 days. Use as flag for downloads.

    #     days_inactive = datetime.now(pytz.utc) - self.last_login
    #     if days_inactive.days < 60:
    #         return True
    #     else:
    #         return False

    # def issub(self, user):
    #     subs = cache.get('%s-subs')
    #     if not subs:
    #         subs = Subscription.objects.filter(userprofile=self).values_list('subscriber', flat=True)
    #         cache.set('%s-subs', subs)

    #     if user.id in subs:
    #         return True
    #     else:
    #         return False

    # def get_absolute_url(self):
    #     return reverse('userprofile_detail', kwargs={'slug':self.slug})

    # def save(self, *args, **kwargs):
    #     if self.user:
    #         self.slug = slugify(self.user.username)
    #     else:
    #         self.slug = slugify(self.username)
    #     super(UserProfile, self).save(*args, **kwargs)

    # @property
    # def profile_image(self):
    #     upi = self.userprofile_images.order_by('-updated')
    #     if upi:
    #         up = upi[0]
    #         url = cache.get('profile_image_%s' % (up.pk))

    #         if url:
    #             return url
    #         else:
    #             url = '%s/convert?w=400&policy=%s&signature=%s' % (up.cdn_url, up.read_policy, up.read_signature)
    #             cache.set('profile_image_%s' % up.pk, url, 60*60*24)
    #             return url
    #     else:
    #         return 'http://placehold.it/400x400&text=No+Profile'

    # @property
    # def thumbnail_image(self):
    #     upi = self.userprofile_images.order_by('-updated')
    #     if upi:
    #         up = upi[0]
    #         url = cache.get('profile_thumbnail_%s' % (up.pk))

    #         if url:
    #             return url
    #         else:
    #             url = '%s/convert?w=100&policy=%s&signature=%s' % (up.cdn_url, up.read_policy, up.read_signature)
    #             cache.set('profile_thumbnail_%s' % up.pk, url, 60*60*24)
    #             return url
    #     else:
    #         return 'http://placehold.it/100x100&text=No+Profile'


    # @property
    # def small_square(self):
    #     upi = self.userprofile_images.order_by('-updated')
    #     if upi:
    #         up = upi[0]
    #         url = cache.get('small_quare_%s' % (up.pk))

    #         if url:
    #             return url
    #         else:
    #             url = '%s/convert?w=100&h=100&fit=crop&policy=%s&signature=%s' % (up.cdn_url, up.read_policy, up.read_signature)
    #             cache.set('small_quare_%s' % up.pk, url, 60*60*24)
    #             return url
    #     else:
    #         return ''

    # @property
    # def list_profile_image(self):
    #     upi = self.userprofile_images.order_by('-updated')
    #     if upi:
    #         up = upi[0]
    #         url = cache.get('listprofile_image_%s' % (up.pk))

    #         if url:
    #             return url
    #         else:
    #             url = '%s/convert?w=400&h=400&align=faces&fit=crop&policy=%s&signature=%s' % (up.cdn_url, up.read_policy, up.read_signature)
    #             cache.set('listprofile_image_%s' % up.pk, url, 60*60*24)
    #             return url
    #     else:
    #         return 'http://placehold.it/400x400&text=No+Profile'

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, newlycreated = UserProfile.objects.get_or_create(user=instance, username=instance.username,created_by=instance,updated_by=instance,slug=instance.username)

post_save.connect(create_user_profile, sender=User)

# def cache_ups(sender, instance, **kwargs):
#     cache.set('ups', UserProfile.objects.all())

# post_save.connect(cache_ups, sender=UserProfile)

# '''
# def create_customer(sender, instance, created, **kwargs):
#     if created:
#        customer = Customer.create(user=instance)

# post_save.connect(create_customer, sender=User)
# '''
class ArtistSubscription(BaseClass):
    user = models.ForeignKey('UserProfile', related_name='user_subscribe')
    artist = models.ForeignKey('UserProfile', related_name='artist_subscribe', verbose_name='Artist')
    date = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=200, blank=True)
    
    
