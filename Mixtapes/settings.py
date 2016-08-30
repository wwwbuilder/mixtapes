"""
Django settings for Mixtapes project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))

# Parse database configuration from $DATABASE_URL
import dj_database_url

if 'LOCAL_DB_PASS' in os.environ:
    ON_LOCAL = True
else:
    ON_LOCAL = False
    
    
#ON_LOCAL = True
DEBUG = False
TEMPLATE_DEBUG = DEBUG

LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/my-profile'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9l0&y70u4iei+%#4&_&)4c8%wo8dcgd4tsd$fp7b_&$n7^vdqi'

# SECURITY WARNING: don't run with debug turned on in production!

ALLOWED_HOSTS = ['.247mixtapes.com', '.app247.herokuapp.com']

ADMINS = (
    ('Ashton Clark', 'ashtonlclark@gmail.com'),
    ('Ryan Clark', 'rclark88@gmail.com'),
)
MANAGERS = ADMINS

# Application definition

INSTALLED_APPS = (
    'suit',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
    'micawber.contrib.mcdjango',
    'phileo',

    #'captcha',
    'agon_ratings',
    'djcelery',
    'gunicorn',
    'grappelli',
    'south',
    'djrill',

    'mptt',
    'guardian',
    'sekizai',
    'rest_framework',
    'locality',
    'django_extensions',
    #'haystack',
    #remember: python manage.py loaddata locality
    'social.apps.django_app.default',
    'django_forms_bootstrap',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # ... include the providers you want to enable:
    #'allauth.socialaccount.providers.dropbox',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    #'allauth.socialaccount.providers.github',
    #'allauth.socialaccount.providers.linkedin',
    #'allauth.socialaccount.providers.openid',
    #'allauth.socialaccount.providers.persona',
    'allauth.socialaccount.providers.soundcloud',
    #'allauth.socialaccount.providers.stackexchange',
    #'allauth.socialaccount.providers.twitch',
    'allauth.socialaccount.providers.twitter',
    #'allauth.socialaccount.providers.vimeo',
    #'allauth.socialaccount.providers.weibo',

    'embed_video',

    #Our own modules
    #'addon',
    '_base',
    '_misc',
    'inkblob',
    'userprofile',
    'mixtape',
    'tweets',
    'region',
    'verify',
    'subscription',
    'audiofield',
    'analytics',
    'payments',
    'preventconcurrentlogin',

)

MIDDLEWARE_CLASSES = (
    'sslify.middleware.SSLifyMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'preventconcurrentlogin.middleware.PreventConcurrentLoginsMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'audiofield.middleware.threadlocals.ThreadLocals',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
)

if not DEBUG:
    MIDDLEWARE_CLASSES += ('django.middleware.cache.FetchFromCacheMiddleware',)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # this is default
    'allauth.account.auth_backends.AuthenticationBackend',
    'guardian.backends.ObjectPermissionBackend',

    #Google
    'social.backends.google.GoogleOpenId',
    'social.backends.google.GoogleOAuth2',
    'social.backends.google.GooglePlusAuth',

    #Twitter
    'social.backends.twitter.TwitterOAuth',

    #Facebook
    'social.backends.facebook.FacebookOAuth2',

    #Instagram
    'social.backends.instagram.InstagramOAuth2',

    #SoundCloud
    'social.backends.soundcloud.SoundcloudOAuth2',

    #Good Old Email
    'social.backends.email.EmailAuth',

    #Default Django... since we use this
    'django.contrib.auth.backends.ModelBackend',

    #phelio like toggling
    'phileo.auth_backends.CanLikeBackend',
)

# Auto logout after 30 minutes of inactivity
SESSION_COOKIE_AGE = 3600
SESSION_SAVE_EVERY_REQUEST = True

ANONYMOUS_USER_ID = -1
ROOT_URLCONF = 'Mixtapes.urls'

WSGI_APPLICATION = 'Mixtapes.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases



DATABASES = {}
if ON_LOCAL:
    DATABASES['default'] = {
        'ENGINE' : 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mixtapes',
        'USER': os.environ['LOCAL_DB_USER'],
        'PASSWORD': os.environ['LOCAL_DB_PASS'],
        #'USER': 'techversant',
        #'PASSWORD': 'tmppassword',
        'HOST': 'localhost',
        'PORT': '5432',
        }
else:
    DATABASES['default'] = dj_database_url.config()

#loading

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Chicago'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, "vendor"),
    os.path.join(PROJECT_DIR, "custom"),
    os.path.join(PROJECT_DIR, "branding"),
    os.path.join(BASE_DIR, "bower_components"),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, "templates"),
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'allauth.account.context_processors.account',
    'allauth.socialaccount.context_processors.socialaccount',
    'mixtape.context_processors.filepicker',
    'mixtape.context_processors.stripe',
    'mixtape.context_processors.tracking_code',
    'mixtape.context_processors.sitewide_slider',
    #'core.context_processors.stripe',
    'sekizai.context_processors.sekizai',

    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
)

#CRISPYFORMS SETTINGS

CRISPY_TEMPLATE_PACK = 'bootstrap3'

#CELERY SETTINGS
#Note, we only have 100 mb of redis.

BROKER_URL = os.getenv('REDISCLOUD_URL', 'redis://localhost:6379')
BROKER_CONNECTION_TIMEOUT = 20
CELERY_RESULT_BACKEND = os.getenv('REDISCLOUD_URL', 'redis://localhost:6379')
CELERY_MESSAGE_COMPRESSION = 'gzip'
CELERY_DISABLE_RATE_LIMITS = True
CELERY_CHORD_PROPAGATES = True
BROKER_POOL_LIMIT = 0
CELERY_REDIS_MAX_CONNECTIONS = 1
#CELERY_SEND_TASK_ERROR_EMAILS = True

# if DEBUG:
#     INSTALLED_APPS += ('debug_toolbar',)

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    #'easy_thumbnails.processors.scale_and_crop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
#LOGGING = {
#    'version': 1,
#    'disable_existing_loggers': False,
#    'filters': {
#        'require_debug_false': {
#            '()': 'django.utils.log.RequireDebugFalse'
#        }
#    },
#    'handlers': {
#        'mail_admins': {
#            'level': 'ERROR',
#            'filters': ['require_debug_false'],
#            'class': 'django.utils.log.AdminEmailHandler'
#        }
#    },
#    'loggers': {
#        'django.request': {
#            'handlers': ['mail_admins'],
#            'level': 'ERROR',
#            'propagate': True,
#        },
#    }
#}
# Log messages to STDERR so that they appear in Heroku log with DEBUG=False
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
        }
    }
}


#Memcachier
def get_cache():
  import os
  try:
    os.environ['MEMCACHE_SERVERS'] = os.environ['MEMCACHIER_SERVERS'].replace(',', ';')
    os.environ['MEMCACHE_USERNAME'] = os.environ['MEMCACHIER_USERNAME']
    os.environ['MEMCACHE_PASSWORD'] = os.environ['MEMCACHIER_PASSWORD']
    return {
      'default': {
        'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
        'TIMEOUT': 500,
        'BINARY': True,
        'OPTIONS': { 'tcp_nodelay': True }
      }
    }
  except:
    return {
      'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
      }
    }

#CACHES = get_cache()
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

#Django-Rest-Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
    ),
    'DEFAULT_RENDERERS': (
        'drf_ujson.renderers.UJSONRenderer',
    ),
}

#Filepicker.io
FILEPICKER_API_KEY = 'AwPujLWPSxypTEyfW3jibz'
FILEPICKER_APP_SECRET = 'SZDTZ73UXVFV7CIZ3UPROGIQUM'

#MANDRILL DJRILL
MANDRILL_API_KEY = "hmmLiYS-ZDb5nbFDgZMJsQ"
EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"
SERVER_EMAIL = "support@247mixtapes.com"
DEFAULT_FROM_EMAIL = "support@247mixtapes.com"

#AMAZON WEB SERVICES
#This is a different CDN than the one filepicker uses...
#CLOUDFRONT_CDN = 'dzw1dwqjk6qq4.cloudfront.net'
CLOUDFRONT_CDN = 'd2pev7u1oknq0a.cloudfront.net'
#FILEPICKER_CLOUDFRONT_CDN = 'cdn.247mixtapes.com'
FILEPICKER_CLOUDFRONT_CDN = 'd2jxt5fbzczsuq.cloudfront.net'
CLOUDFRONT_KEYPAID_ID = 'APKAJAQXBMJWMEON363A'

#if CLOUDFRONT_CDN:
    #AWS_S3_CUSTOM_DOMAIN = CLOUDFRONT_CDN

FILEPICKER_STORE_API = 'https://www.filepicker.io/api/store'

#Filepicker Storage to mixtapes247 bucket
FILEPICKER_ACCESS_KEY_ID = 'AKIAIYGRCMTBICBEZIFQ'
FILEPICKER_SECRET_ACCESS_KEY = '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'
FILEPICKER_STORAGE_BUCKET_NAME = 'mixtapes247'

#This is a different bucket than the one filepicker stores to...
AWS_ACCESS_KEY_ID = 'AKIAIYJ7RIQXEEZAJPJA'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = '247static'

AWS_IS_GZIPPED = True
AWS_QUERYSTRING_AUTH = False

# see http://developer.yahoo.com/performance/rules.html#expires
AWS_HEADERS = {
    'Expires': 'Thu, 19 Apr 2040 20:00:00 GMT',
    'Cache-Control': 'max-age=86400',
}

# if DEBUG:
#     TWILIO_ACCOUNT = 'AC426961059d5aa66d49a68c50bed97ec7'
#     TWILIO_TOKEN = '4d9e94f2c4fda27981273f7ae909a2e9'
#     TWILIO_NUMBER = '+15005550006'

# else:
TWILIO_ACCOUNT = 'ACecdc0ec61675214411ff50e3ce2dec93'
TWILIO_TOKEN = 'd23e3789825f8ef231c3fa76e50b6e99'
TWILIO_NUMBER = '3126464247'


#django-sslify for https secure-url
#########################################
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


#disable-sslify

#SSLIFY_DISABLE = True


'''SOCIAL AUTH SETTINGS'''
############################################
from django.core.urlresolvers import reverse_lazy

SOCIAL_AUTH_LOGIN_REDIRECT_URL = reverse_lazy('home')
#Used to redirect the user once the auth process ended successfully. The value of ?next=/foo is used if it was present

SOCIAL_AUTH_LOGIN_ERROR_URL = reverse_lazy('login-error')
#URL where the user will be redirected in case of an error

SOCIAL_AUTH_LOGIN_URL = reverse_lazy('login')
#Is used as a fallback for LOGIN_ERROR_URL

SOCIAL_AUTH_NEW_USER_REDIRECT_URL = reverse_lazy('my-account')
#Used to redirect new registered users, will be used in place of SOCIAL_AUTH_LOGIN_REDIRECT_URL if defined.

SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = reverse_lazy('my-connections')
#Like SOCIAL_AUTH_NEW_USER_REDIRECT_URL but for new associated accounts (user is already logged in). Used in place of SOCIAL_AUTH_LOGIN_REDIRECT_URL

SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = reverse_lazy('my-connections')
#The user will be redirected to this URL when a social account is disconnected

SOCIAL_AUTH_INACTIVE_USER_URL = reverse_lazy('inactive')
#Inactive users can be redirected to this URL when trying to authenticate.

SOCIAL_AUTH_USER_MODEL = 'auth.User'
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True

#Facebook local
#SOCIAL_AUTH_FACEBOOK_KEY = '835626976447547'#'414105495351675' #835626976447547
#SOCIAL_AUTH_FACEBOOK_SECRET = 'fac09a361ea96ad71eed880065659393'
#SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']

#Facebook on heroku
SOCIAL_AUTH_FACEBOOK_KEY = '1512936935589178'#'414105495351675' #835626976447547
SOCIAL_AUTH_FACEBOOK_SECRET = 'c076dcc91d921d796dbba8cc1f466c9e'
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']

#Google
SOCIAL_AUTH_GOOGLE_KEY = 'AIzaSyCxtSz1bsnEtxQS6h0fwC2f_P6DLWxOeRc'
SOCIAL_AUTH_GOOGLE_ClIENT_ID = '1039398081604-c76n51jp01sk7bmtmg485crptj76n6aa.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_SECRET = 'ihNK-pijJfYYkoRBjKgWn6fc'

#Twitter
SOCIAL_AUTH_TWITTER_KEY = 'zcPK6GIW8S4ryk4mpNyHlEbUJ'
SOCIAL_AUTH_TWITTER_SECRET = 'xKOvTMZQ3VBJ1HFpzDLscPZ49D0Hj5AuaNWbIrNKI3bTYHqzJI'

#Twitter Test (@247mixtest)
TWITTER_CONSUMER_KEY = 'fPLf2C4kwhJ4QMBrpXa9fbb9m'
TWITTER_CONSUMER_SECRET = 'eey66KS1GwbjsjqMcL4rfLJaX2V8epEO4OM07hYk7C6S2LMEk9'

#Twitter Production (@247Mixtapes)
#TWITTER_CONSUMER_KEY = 'BvWr1TT7VdI8bVHORk0A0ZFVQ'
#TWITTER_CONSUMER_SECRET = 'rfOt4u5m21ktdkp5bFvHkov36og0v9CcI26vjhcJuho6dFuUl8'
############################################

# Static asset configuration

if ON_LOCAL:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
    STATIC_URL = '/static/'
    MEDIA_URL ='/media/'
else:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    #STATIC_URL = 'https://static.247mixtapes.com/'
    #MEDIA_URL = 'https://static.247mixtapes.com/'
    STATIC_URL = 'https://dak6fnryqg5ij.cloudfront.net/'
    MEDIA_URL = STATIC_URL

STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')

ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

#Media files configuration
MEDIA_ROOT = os.path.join(PROJECT_DIR, "media")
MEDIA_UPLOAD_ROOT = os.path.join(MEDIA_ROOT, "uploads")

TEMP_ROOT = os.path.join(PROJECT_DIR, "temp_media")

#Bitly
BITLY_TOKEN = '334f893cc1559d0f11bd81d3b0462e1b208d5544'

#SOUNDCLOUD SETTINGS
SC_ID = '0f334ddc5f6987c9c9d9ef686759986e'
SC_SECRET = '034493ec72301db4629c04df7f518666'
SC_USERNAME = '247mixtapes'
SC_PASSWORD = '{Js2Cnd'

#STRIPE ACCOUNT
STRIPE_TEST = True

if STRIPE_TEST == True:
    STRIPE_PUBLIC_KEY = 'pk_test_dELcQOZlmIhfc3tMeb7AoDGd'
    STRIPE_SECRET_KEY = 'sk_test_g7kiChcHhuOusUAx6AoJA3yf'

else:
    STRIPE_PUBLIC_KEY = 'pk_live_a36dzIJNmOtxyia7JdRNtsYP'
    STRIPE_SECRET_KEY = 'sk_live_DbpeCp8fNw8U1vrxSQJWpZUC'

PAYMENTS_INVOICE_FROM_EMAIL = 'billing@247mixtapes.com'
PAYMENTS_PLANS = {
    "monthly": {
        "stripe_plan_id": "premium-monthly",
        "name": "Monthly ($5/month)",
        "description": "Unlimited premium downloads and streams for 1 month.",
        "price": 5,
        "currency": "usd",
        "interval": "month"
    },
    "yearly": {
        "stripe_plan_id": "premium-yearly",
        "name": "Yearly ($50/year)",
        "description": "Unlimited premium downloads and streams for 1 year.",
        "price": 50,
        "currency": "usd",
        "interval": "year"
    },
   "premium-publisher-monthly": {
        "stripe_plan_id": "premium-publisher-monthly",
        "name": "premium-publisher-monthly($10/month)",
        "description": "Unlimited mixtape uploads and other upgrades for 1 month.",
        "price": 10,
        "currency": "usd",
        "interval": "month"
    },
    "premium-publisher-yearly": {
        "stripe_plan_id": "premium-publisher-yearly",
        "name": "premium-publisher-yearly($100/year)",
        "description": "Unlimited mixtape uploads and other upgrades for 1 year.",
        "price": 100,
        "currency": "usd",
        "interval": "year"
    }
}
PAYMENTS_DEFAULT_PLAN = {
    "monthly": {
        "stripe_plan_id": "premium-monthly",
        "name": "Monthly ($5/month)",
        "description": "Unlimited premium downloads and streams for 1 month.",
        "price": 5,
        "currency": "usd",
        "interval": "month"
    },
    "yearly": {
        "stripe_plan_id": "premium-yearly",
        "name": "Yearly ($50/year)",
        "description": "Unlimited premium downloads and streams for 1 year.",
        "price": 50,
        "currency": "usd",
        "interval": "year"
    },
   "premium-publisher-monthly": {
        "stripe_plan_id": "premium-publisher-monthly",
        "name": "premium-publisher-monthly($10/month)",
        "description": "Unlimited mixtape uploads and other upgrades for 1 month",
        "price": 10,
        "currency": "usd",
        "interval": "month"
    },
    "premium-publisher-yearly": {
        "stripe_plan_id": "premium-publisher-yearly",
        "name": "premium-publisher-yearly($90/year)",
        "description": "Unlimited mixtape uploads and other upgrades for 1 year.",
        "price": 100,
        "currency": "usd",
        "interval": "year"
    }
}
DEFAULT_PLAN = None
#DEFAULT_PLAN = {
    #"monthly": {
        #"stripe_plan_id": "premium-monthly",
        #"name": "Monthly ($8/month)",
        #"description": "Unlimited, premium downloads for 1 month.",
        #"price": 8,
        #"currency": "usd",
        #"interval": "month"
    #},
    #"yearly": {
        #"stripe_plan_id": "premium-yearly",
        #"name": "Yearly ($50/year)",
        #"description": "Unlimited, premium downloads for 1 year.",
        #"price": 50,
        #"currency": "usd",
        #"interval": "year"
    #},
   #"premium-publisher-monthly": {
        #"stripe_plan_id": "premium-publisher-monthly",
        #"name": "premium-publisher-monthly($9/month)",
        #"description": "Unlimited, premium downloads for 1 month.",
        #"price": 9,
        #"currency": "usd",
        #"interval": "month"
    #},
    #"premium-publisher-yearly": {
        #"stripe_plan_id": "premium-publisher-yearly",
        #"name": "premium-publisher-yearly($90/year)",
        #"description": "Unlimited, premium downloads for 1 year.",
        #"price": 90,
        #"currency": "usd",
        #"interval": "year"
    #}
#}


#ZENDESK SETTINGS
ZENDESK_API_SECRET = 'd732f1608c91db0b16e6069c7c5b2b84001fa086c2646019554fae933ed7673e'

#GRAPPELLI SETTINGS
GRAPPELLI_ADMIN_TITLE = '24/7 Mixtapes'

#Debug Toolbar Settings
INTERNAL_IPS = ('127.0.0.1',)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

SITE_ID = 0

ACCOUNT_SIGNUP_FORM_CLASS = 'mixtape.forms.SignupForm'
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[24/7Mixtapes]'
PHILEO_LIKABLE_MODELS = {
        "mixtape.Mixtape": {}  # can override default config settings for each model here
}


SOCIALACCOUNT_PROVIDERS = \
    { 'google':
        { 'SCOPE': ['https://www.googleapis.com/auth/userinfo.profile'],
          'AUTH_PARAMS': { 'access_type': 'online' } }}

# Django Suit configuration example
SUIT_CONFIG = {
	# header
	'ADMIN_NAME': '24/7 Mixtapes',
	# 'HEADER_DATE_FORMAT': 'l, j. F Y',
	# 'HEADER_TIME_FORMAT': 'H:i',

	# forms
	# 'SHOW_REQUIRED_ASTERISK': True,  # Default True
	# 'CONFIRM_UNSAVED_CHANGES': True, # Default True

	# menu
	# 'SEARCH_URL': '/admin/auth/user/',
	'MENU_ICONS': {
		'sites': 'icon-leaf',
		'auth': 'icon-lock',
		'core': 'icon-cog',
		'cms': 'icon-edit',
		'socialaccount': 'icon-user',
		'payments': 'icon-shopping-cart',
		'tweets': 'icon-pencil',
		'account': 'icon-envelope',
		'phileo': 'icon-thumbs-up',
	},
	# 'MENU_OPEN_FIRST_CHILD': True, # Default True
	# 'MENU_EXCLUDE': ('auth.group',),
	# 'MENU': (
	#     'sites',
	#     {'app': 'auth', 'icon':'icon-lock', 'models': ('user', 'group')},
	#     {'label': 'Settings', 'icon':'icon-cog', 'models': ('auth.user', 'auth.group')},
	#     {'label': 'Support', 'icon':'icon-question-sign', 'url': '/support/'},
	# ),

	# misc
	# 'LIST_PER_PAGE': 15
}

# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'xapian_backend.XapianEngine',
#         'PATH': os.path.join(os.path.dirname(__file__), 'xapian_index'),
#     },
# }

USE_TZ = True

#RECAPTCHA_PUBLIC_KEY = '6LcXOPgSAAAAAMhmvDE9KTRHW2HnHDYyp_i2FgxE'
#RECAPTCHA_PRIVATE_KEY = '6LcXOPgSAAAAAMmOwAXkE0iAfnwPVEq8dK7--Gnj'
RECAPTCHA_PUBLIC_KEY = '6LftVPwSAAAAAK0wOBNzjbt6juGZO5vsD9LYscIS'
RECAPTCHA_PRIVATE_KEY = '6LftVPwSAAAAADS3FUV34mrHynu0dg0Nv2ccYVbo'

try:
    from local_settings import *
except ImportError:
    pass

SEND_EMAIL_RECEIPTS = None
#INVOICE_FROM_EMAIL = getattr(
    #settings,
    #"PAYMENTS_INVOICE_FROM_EMAIL",
    #"billing@example.com"
#)
PAYMENTS_TRIAL_PERIOD_FOR_USER_CALLBACK = None
TRIAL_PERIOD_FOR_USER_CALLBACK =None
PLAN_CHOICES = [
    (plan, PAYMENTS_PLANS[plan].get("name", plan))
    for plan in PAYMENTS_PLANS
]
if isinstance(TRIAL_PERIOD_FOR_USER_CALLBACK, basestring):
    TRIAL_PERIOD_FOR_USER_CALLBACK = load_path_attr(
        TRIAL_PERIOD_FOR_USER_CALLBACK
    )
PLAN_QUANTITY_CALLBACK = None
if isinstance(PLAN_QUANTITY_CALLBACK, basestring):
    PLAN_QUANTITY_CALLBACK = load_path_attr(PLAN_QUANTITY_CALLBACK)

def plan_from_stripe_id(stripe_id):
    for key in PAYMENTS_PLANS.keys():
        if PAYMENTS_PLANS[key].get("stripe_plan_id") == stripe_id:
            return key

