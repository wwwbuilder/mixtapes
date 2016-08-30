from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import models
from django.db.models.signals import *
from django.utils.translation import ugettext as _
from django.utils.text import slugify

from .mixins import *
from mptt.models import MPTTModel, TreeForeignKey

import hmac
import hashlib
import time
import base64
import ujson as json
import time

class BaseMPTTModel(MPTTModel):
	'''
	This contains MPTT functionality.
	'''
	parent = TreeForeignKey('self', blank=True, null=True, related_name='children')

	class Meta:
		abstract = True

class BaseClass(BaseMPTTModel, BaseMixin):
	pass
	class Meta:
		abstract = True

	def get_content_type_id(self):
		return ContentType.objects.get_for_model(self).id

class GenericFKBaseClass(BaseClass, GenericFKMixin):
	pass
	class Meta:
		abstract = True

# def getuserprofiles():
# 	ups = cache.get('ups')
# 	if not ups:
# 		ups = UserProfile.objects.all()
# 		cache.set('ups', ups)
# 	return ups

# def getpolicy(policytype):
# 	pol = cache.get(policytype)
# 	if pol:
# 		return pol
# 	else:
# 		secret = settings.FILEPICKER_APP_SECRET
# 		if secret:
# 			if policytype == 'deletepolicy':
# 				expiry = 60*5
# 			else:
# 				expiry = 60*60*24

# 			#Set the calls options for each policy here
# 			if policytype == 'uploadpolicy':
# 				calls = ['pick', 'store']
# 			elif policytype == 'readpolicy':
# 				calls = ['read', 'convert']
# 			elif policytype == 'deletepolicy':
# 				calls = ['remove']

# 			polexp = int(time.time() + expiry)
# 			json_policy = json.dumps({'expiry': polexp, 'call':calls})
# 			policy = base64.urlsafe_b64encode(json_policy)
# 			#Set the cache to expire earlier
# 			cache.set(policytype, policy, 60*60*12)
# 			return policy
# 		else:
# 			return ''

# def getsignature(signaturetype):
# 	sig = cache.get(signaturetype)
# 	if sig:
# 		return sig

# 	else:
# 		secret = settings.FILEPICKER_APP_SECRET
# 		if secret:
# 			if signaturetype == 'deletesignature':
# 				expiry = 60*10
# 			else:
# 				expiry = 60*60*24*7

# 			if signaturetype == 'uploadsignature':
# 				policy = getpolicy('uploadpolicy')
# 			elif signaturetype == 'readsignature':
# 				policy = getpolicy('readpolicy')
# 			elif signaturetype == 'deletesignature':
# 				policy = getpolicy('deletepolicy')

# 			sig = hmac.new(secret, policy, hashlib.sha256).hexdigest()
# 			cache.set(signaturetype, sig, expiry)
# 			return sig
# 		else:
# 			return ''

