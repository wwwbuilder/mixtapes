import hmac
from datetime import time
from django.core.cache import cache
from django.conf import settings
from django.db import models
from _base.models import BaseClass, GenericFKBaseClass
from .utils import *

class InkBlob(BaseClass):
    url = models.URLField()
    filename = models.CharField(max_length=200)
    mimetype = models.CharField(max_length=200, blank=True)
    size = models.BigIntegerField(blank=True, null=True)
    isWriteable = models.BooleanField(blank=True)
    key = models.CharField(max_length=300, blank=True)

    class Meta(BaseClass.Meta):
        abstract = True
    
    
    @property
    def normal_url(self):
        if self.url:
            url = self.url
        else:
            url = ""
        return url
    
    @property
    def cdn_url(self):
        if settings.FILEPICKER_CLOUDFRONT_CDN:
            url = self.url.replace('www.filepicker.io', settings.FILEPICKER_CLOUDFRONT_CDN)
        else:
            url = self.url
        return url
    
    #aws_url
    @property
    def aws_url(self):
	url_path = "%s" %(self.key)
	url = 'https://cdn.247mixtapes.com/%s' %(url_path)
	return url    
    
    @property
    def signed_url(self):
        if self.url:
            from django.utils.http import urlquote
            url_path = urlquote(self.key, safe=',/?:@&=+$#')
            url_aws_path = 'http://cdn.247mixtapes.com/%s' %(url_path)
            secs = 180 #seconds
            track_url = get_signed_url(url_path,url_aws_path,secs)
        else:
            track_url = ""
        return track_url
        

    @property
    def secure_url(self):
        if settings.FILEPICKER_APP_SECRET:
            url = self.cdn_url
            url = url + '?signature=%s&policy=%s' % (getsignature('read'), getpolicy('read'))

        else:
            url = self.url
        return url       

    @property
    def display_order(self):
        try:
            return self.order + 1
        except:
            return 1

    # def secure_url(self):
    #     if settings.FILEPICKER_APP_SECRET:
    #         url = self.cdn_url
    #         url = url + '?signature=%s&policy=%s' % (self.signature, self.policy)

    #     else:
    #         url = self.url
    #     return url

    # def policy(self):
    #     handle = self.url.split('file/')[1]
    #     pol = cache.get('policy-%s' % handle)
    #     #print '\n%s\n' % pol
    #     if pol:
    #         return pol
    #     else:
    #         if settings.FILEPICKER_APP_SECRET:
    #             secret = settings.FILEPICKER_APP_SECRET
    #             expiry = int(time.time() + 60*20)
    #             json_policy = json.dumps({'handle': handle, 'expiry': expiry})
    #             #print '\n%s\n' % json_policy
    #             policy = base64.urlsafe_b64encode(json_policy)
    #             #print '\n%s\n' % policy
    #             cache.set('policy-%s' % handle, policy, 60*19)
    #             return policy
    #         else:
    #             return ''

    # def signature(self):
    #     handle = self.url.split('file/')[1]
    #     sig = cache.get('signature-%s' % handle)
    #     if sig:
    #         #print 'FOUND IN CACHE!!!'
    #         return sig

    #     else:
    #         #print 'NOT IN CACHE!!!'
    #         if settings.FILEPICKER_APP_SECRET:
    #             secret = settings.FILEPICKER_APP_SECRET
    #             policy = self.policy
    #             sig = hmac.new(secret, policy, hashlib.sha256).hexdigest()
    #             cache.set('signature-%s' % handle, sig, 60*20)
    #             return sig
    #         else:
    #             return ''

    # @property
    # def small_profile_image(self):
    #     url = cache.get('%s_small_profile_%s' % (self.__class__.__name__, self.pk))
    #     if url:
    #         return url
    #     else:
    #         url = '%s/convert?w=150&h=150&policy=%s&signature=%s' % (self.cdn_url, self.read_policy, self.read_signature)
    #         cache.set('%s_small_profile_%s' % (self.__class__.__name__, self.pk), url, 60*60*24)
    #         return url

    # @property
    # def slider_image(self):
    #     try:
    #         cov = cache.get('slider_image-%s' % self.id)
    #         if cov:
    #             return cov
    #         else:
    #             cov = '%s/convert?w=762&h=429&fit=clip&policy=%s&signature=%s&format=jpg' % (self.cdn_url, self.read_policy, self.read_signature)
    #             cache.set('slider_image-%s' % self.pk, cov, 60*60)
    #             return cov

    #     except:
    #         return 'http://placehold.it/762&text=No+Image!'
    
    


    def __unicode__(self):
        return '%s: %s' % (self.mimetype, self.filename)
