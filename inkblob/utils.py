import hmac, hashlib, time, base64
try:
    import ujson as json
except:
    import json

from django.conf import settings
from django.core.cache import cache
import boto, time, pprint
from boto import cloudfront
from boto.cloudfront import distribution
from retrying import retry

def getpolicy(policytype):
    #pol = cache.get('%s-policy' % policytype)
    pol = ""
    if pol:
        return pol
    else:
        secret = settings.FILEPICKER_APP_SECRET
        if secret:
            if policytype == 'delete':
                expiry = 60*5
            else:
                expiry = 60*60*24

            #Set the calls options for each policy here
            if policytype == 'upload':
                calls = ['pick', 'store']
                expiry = 60*60*24
                
            elif policytype == 'download':
                calls = ['pick', 'store']
            elif policytype == 'read':
                calls = ['read', 'convert']
            elif policytype == 'delete':
                calls = ['remove']

            polexp = int(time.time() + expiry)
            json_policy = json.dumps({'expiry': polexp, 'call':calls})
            policy = base64.urlsafe_b64encode(json_policy)
            #Set the cache to expire earlier
            cache.set('%s-policy' % policytype, policy, expiry)
            return policy
        else:
            return ''

def getsignature(signaturetype):
    #sig = cache.get('%s-signature' % signaturetype)
    sig = ""
    if sig:
        return sig

    else:
        secret = settings.FILEPICKER_APP_SECRET
        if secret:
            if signaturetype == 'delete':
                expiry = 60*10
            else:
                expiry = 60*60*24

            if signaturetype == 'upload':
                policy = getpolicy('upload')
            elif signaturetype == 'download':
                policy = getpolicy('download')            
            elif signaturetype == 'read':
                policy = getpolicy('read')
            elif signaturetype == 'delete':
                policy = getpolicy('delete')

            sig = hmac.new(secret, policy, hashlib.sha256).hexdigest()
            cache.set('%s-signature' % signaturetype, sig, expiry)
            return sig
        else:
            return ''
        

### This functions creates a signed url which will restrict users from accessing the content in your s3 bucket from third party
#plugins.
#the boto framework is provided by Amazon as a way to allow access to cloudfront using any python framework
#The keys are the ones associated with the particular AWS account and are given on creation of the account
#The distribution refers to the web distribution to be used for restricting the unauthorized access to the content

###

@retry
def get_signed_url(object_name_url,object_url,seconds):
    
    #import pdb;pdb.set_trace()
    AWS_ACCESS_KEY_ID = 'AKIAJSSGCYWIFQMOCXHQ'
    AWS_SECRET_ACCESS_KEY = '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'
    KEYPAIR_ID = 'APKAJ2JCIS6POSQU2IHA'
    KEYPAIR_FILE = 'pk-APKAJ2JCIS6POSQU2IHA.pem'
    CF_DISTRIBUTION_ID = 'E3DMF43RAW1UH5'  #distribution for static247.s3.amazonaws.com
    #for filepicker.io the distribution id is E3DMF43RAW1UH5
    #both are configured to use signed url
    
    #connecting to the aws  cloudfront service
    my_connection = boto.cloudfront.CloudFrontConnection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    #getting the web  distributions
    distros = my_connection.get_all_distributions()
    
    #creating an origin access identity to associate with the distribution.it specifies who has access to modify the content
    oai = my_connection.create_origin_access_identity('my_oai', 'An OAI for testing')
    
    distribution_config = my_connection.get_distribution_config(CF_DISTRIBUTION_ID)
    distribution_info = my_connection.get_distribution_info(CF_DISTRIBUTION_ID)
    my_distro = boto.cloudfront.distribution.Distribution(connection=my_connection, config=distribution_config,domain_name=distribution_info.domain_name, id=CF_DISTRIBUTION_ID, last_modified_time=None, status='Active')
    #S3 connection 
    s3 = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    #s3 bucket name. Can be the mixtapes247 or static247
    BUCKET_NAME = "mixtapes247"
    bucket = s3.get_bucket(BUCKET_NAME)
    #content to add a signed url. must be a full  url excluding the the S3 dormain name
    object_name = object_name_url
    key = bucket.get_key(object_name)
    #key.add_user_grant("READ", oai.s3_user_id)
    #time for the url to expire .Can be set to none 
    SECS = seconds #10hrs
    OBJECT_URL = object_url
    #the signd url to serve to clients
    my_signed_url = my_distro.create_signed_url(OBJECT_URL,KEYPAIR_ID,expire_time=int(time.time()) + SECS,private_key_file=KEYPAIR_FILE)
    
    if my_signed_url:
        return my_signed_url
    else:
        return ""