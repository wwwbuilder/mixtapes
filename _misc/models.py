from django.core.cache import cache
from django.db import models
from django.utils.translation import ugettext as _

from inkblob.models import *
from inkblob.utils import getpolicy, getsignature , get_signed_url
from _base.models import *

class Image(InkBlob, GenericFKMixin):
	
	class Meta(InkBlob.Meta):
		verbose_name = _('Image')
		verbose_name_plural = _('Images')

	def get_thumbnail(self, width=100, height=100):
# 		url = cache.get('%s_thumbnail_%s_%sx%s' % (self.__class__.__name__, self.pk, width, height))
# 		if not url:
# 			url = '%s/convert?w=%s&h=%s' % (self.cdn_url, width, height)
# 			cache.set('%s_thumbnail_%s_%sx%s' % (self.__class__.__name__, self.pk, width, height), url, 60*60*24)
#		return url
		return self.default_url
		
	def get_image(self, width=200, height=200):
# 		url = cache.get('%s_thumbnail_%s_%sx%s' % (self.__class__.__name__, self.pk, width, height))
# 		if not url:
# 			url = '%s/convert?w=562&h=399&fit=crop&format=jpg' % (self.cdn_url)
# 			cache.set('%s_thumbnail_%s_%sx%s' % (self.__class__.__name__, self.pk, width, height), url, 60*60*24)
#		return url
		return self.default_url
		
#	def get_userprofile_list_image(self, width=200, height=200):
#		url = cache.get('%s_thumbnail_%s_%sx%s' % (self.__class__.__name__, self.pk, width, height))
#		if not url:
#			url = '%s/convert?w=%s&h=%s&policy=%s&signature=%s' % (self.cdn_url, width, height, getpolicy('read'), getsignature('read'))
#			cache.set('%s_thumbnail_%s_%sx%s' % (self.__class__.__name__, self.pk, width, height), url, 60*60*24)
#		return url
			
	def slider_image(self):
		try:
			cov = cache.get('slider_image-%s' % self.id)
			if cov:
				return cov
			else:
				#cov = '%s/convert?w=900&h=399&fit=crop&format=jpg' % (self.cdn_url)
				image_path = "%s" %(self.key)
				image_aws_path = 'https://cdn.247mixtapes.com/%s' %(image_path)
				secs = 180
				cov = get_signed_url(image_path,image_aws_path,secs)
				cache.set('slider_albumcover-%s' % self.id, cov, 60*60)
				return cov

		except:
			return 'https://placehold.it/900&text=No+Image!'

	# unsigned images urls everywhere
	@property
	def default_url(self):
		return self.aws_url
