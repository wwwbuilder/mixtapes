from .models import *
from django.contrib import admin

class TweetAdmin(admin.ModelAdmin):
	list_display = ('tweet_url', 'created', 'mixtape', 'tweet_artist', 'tweet_producer', 'tweet_dj', 'body',)
	list_editable = ('tweet_artist', 'tweet_producer', 'tweet_dj', 'body',)
	list_display_links = ('created',)
	fields = ('mixtape', 'body', 'primaryProducer', 'primaryDJ', 'tweet_artist', 'tweet_producer', 'tweet_dj',)


admin.site.register(Tweet, TweetAdmin)