from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.template.defaultfilters import slugify
from django.contrib.sites.models import get_current_site
from django.contrib.sites.models import Site
from twython import Twython
import requests
import bitly_api as bitly
from cStringIO import StringIO
import twitter
#from mixtape.models import Userprofile

def get_bitly_api():
	c = bitly.Connection(access_token=settings.BITLY_TOKEN)
	return c

def return_api():
	twitter = Twython(
		settings.TWITTER_CONSUMER_KEY,
		settings.TWITTER_CONSUMER_SECRET,
		cache.get('final_oauth_token'),
		cache.get('final_oauth_token_secret')
		)
	return twitter

def manual_get_tokens():
	twitter = Twython(
		settings.TWITTER_CONSUMER_KEY,
		settings.TWITTER_CONSUMER_SECRET,
		)
	try:
		auth = twitter.get_authentication_tokens()
	except Exception,e:
		print e
	print auth
	oauth_token = auth['oauth_token']
	oauth_token_secret = auth['oauth_token_secret']
	print '\nGo to this url and get the PIN number: %s' % auth['auth_url']
	pin = input('What is the PIN?')

	twitter = Twython(
		settings.TWITTER_CONSUMER_KEY,
		settings.TWITTER_CONSUMER_SECRET,
		oauth_token,
		oauth_token_secret
		)
	final = twitter.get_authorized_tokens(pin)
	final_oauth_token = final['oauth_token']
	final_oauth_token_secret = final['oauth_token_secret']
	cache.set('final_oauth_token', final_oauth_token, 60*60*24*365)
	cache.set('final_oauth_token_secret', final_oauth_token_secret, 60*60*24*365)

def get_tokens():
	twitter = Twython(
		settings.TWITTER_CONSUMER_KEY,
		settings.TWITTER_CONSUMER_SECRET,
		)
	auth = twitter.get_authentication_tokens()
	oauth_token = auth['oauth_token']
	oauth_token_secret = auth['oauth_token_secret']
	cache.set('oauth_token', oauth_token, 60*60*12)
	cache.set('oauth_token_secret', oauth_token_secret, 60*60*12)
	currentsite = Site.objects.get_current().domain

	#send_mail(
		#'IMPORTANT: UPDATE TWITTER PIN!',
		#'Our twitter PIN may have expired. \nPlease go to this url: %s and update the pin in our admin section (http://%s%s)' % (auth['auth_url'], currentsite, reverse('admin:tweets_authorization_changelist')),
		#'important@247mixtapes.com',
		#['terryhong@gmail.com', 'rclark88@gmail.com',]
		#)

def get_api():
	if not cache.get('final_oauth_token') and not cache.get('final_oauth_token_secret'):
		get_tokens()
	return return_api()

class BaseClass(models.Model):
	updated = models.DateTimeField(auto_now=True)
	created = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(User, blank=True, null=True)

	order = models.PositiveIntegerField(blank=True, null=True)
	title = models.CharField(max_length=200, blank=True)
	slug = models.SlugField(max_length=200, blank=True)	

	class Meta:
		abstract = True
		ordering = ['order']

	def __unicode__(self):
		return ('%s: %s') % (self.created_by, self.created)

	def save(self, *args, **kwargs):
		self.title = self.title.title()
		self.slug = slugify(self.title)
		super(BaseClass, self).save(*args, **kwargs)

	def isCreator(self, user_obj):
		'''
		Checks if the given user_obj is the creator of the objects
		'''
		return self.created_by == user_obj

class Tweet(BaseClass):
	mixtape = models.ForeignKey('mixtape.Mixtape', related_name='tweets')
	body = models.TextField(blank=True, max_length=140)

	primaryProducer = models.ForeignKey('userprofile.UserProfile', blank=True, null=True, related_name='producer_tweets')
	primaryDJ = models.ForeignKey('userprofile.UserProfile', blank=True, null=True, related_name='dj_tweets')

	tweet_artist = models.BooleanField(default=True, verbose_name=u'Tweet Artist Handle')	
	tweet_producer = models.BooleanField(default=True, verbose_name=u'Tweet Producer Handle')
	tweet_dj = models.BooleanField(default=True, verbose_name=u'Tweet DJ Handle')	

	tweet_id = models.BigIntegerField(blank=True, null=True)
	tweet_url = models.URLField(blank=True)

	class Meta:
		verbose_name = 'Tweet'
		verbose_name_plural = 'Tweets'

	def __unicode__(self):
		return self.mixtape.name

	@property
	def artist_handle(self):		
		pa = self.mixtape.primaryArtist
		if self.tweet_artist and pa.twitter:
			return '@%s' % pa.twitter.split('//twitter.com/')[-1]
		else:
			return '%s' % pa.username

	@property
	def producer_handle(self):
		pp = self.primaryProducer
		if selt.tweet_producer and pp.twitter:		
			return '@%s' % pp.twitter.split('//twitter.com/')[-1]
		else:
			try:
				return '%s' % pp.username
			except:
				return ''

	@property
	def dj_handle(self):
		pdj = self.primaryDJ
		if selt.tweet_dj and pdj.twitter:		
			return '@%s' % pdj.twitter.split('//twitter.com/')[-1]
		else:
			try:
				return '%s' % pdj.username
			except:
				return ''				

	@classmethod
	def maketweet(cls, mixtape):
		#Create list of artist, producer, and dj handles

		t = Tweet(
				mixtape = mixtape
			)
		t.save()
		print 'Tweet created: %s' % t.body

	@classmethod
	def tweetout(cls, tweet):
		if tweet.mixtape.approved:
			#twitter = get_api()
			bitly = get_bitly_api()
			currentsite = Site.objects.get_current().domain
			mixtapeurl = 'http://%s%s' % (currentsite, tweet.mixtape.get_absolute_url())
			shorturl = bitly.shorten(mixtapeurl)['url']

			if tweet.body:
				status = tweet.body
			else:
				status = 'New #mixtape: %s - %s (%s)' % (tweet.mixtape.name, tweet.artist_handle, shorturl)

			try:
				api= twitter.Api(consumer_key=settings.TWITTER_CONSUMER_KEY,
					     consumer_secret=settings.TWITTER_CONSUMER_SECRET,
					     access_token_key=settings.TWITTER_APP_KEY,
					     access_token_secret=settings.TWITTER_APP_SECRET)
				
				if tweet.mixtape.get_mixtape_thumnail():
					#img = requests.get(url=tweet.mixtape.get_mixtape_thumnail()).content
					tw = api.PostMedia(status, tweet.mixtape.mixtape_image())

					print 'Attaching mixtape cover image to tweet!'

				else:
					tw = api.PostUpdate(status)

				print 'Mixtape tweeted!'

				tweet.tweet_id = tw.id
				tweet.tweet_url = 'https://twitter.com/%s/status/%s' % (tw.user.screen_name, tw.id)
				tweet.save()
				print '\nSUCCESS: %s\n' % status

			except:
				print 'Something wrong with the tweet!'
		else:
			print '\nMixtape not yet admin approved!'

	def save(self, *args, **kwargs):

		if self.mixtape.approved and not self.tweet_id:
			Tweet.tweetout(self)
		super(Tweet, self).save(*args, **kwargs)

class Authorization(models.Model):
	pin = models.IntegerField()

	# def save(self, *args, **kwargs):

	#OVERIDE THE SAVE HERE TO UPDATE THE FINAL OAUTH TOKEN KEY AND SECRET IN THE CACHE
	# 	if self.mixtape.approved and not self.tweet_id:
	# 		Tweet.tweetout(self)
	# 	super(Authorization, self).save(*args, **kwargs)
