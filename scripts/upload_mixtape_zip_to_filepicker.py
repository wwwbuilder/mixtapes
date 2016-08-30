import subprocess
import os
import shutil
from django.conf import settings
from mixtape.models import *

from subprocess import CalledProcessError

import urllib
import json
import sys
import os
import ConfigParser
import argparse
import time
import hmac, hashlib, time, base64


#######################
# Constants
FPURL = "https://www.filepicker.io"
CDN_URL = 'https://cdn.247mixtapes.com/'
FPAPIURL = "https://developers.filepicker.io"
CONFIG_FILE = os.path.expanduser('~/.geturl')

#######################
# Loading Config
APIKEY = settings.FILEPICKER_API_KEY


#def check_output(*popenargs, **kwargs):
#    import pdb;pdb.set_trace()
#    import subprocess
#    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
#    output, unused_err = process.communicate()
#    retcode = process.poll()
#    if retcode:
#       cmd = kwargs.get("args")
#       if cmd is None:
#          cmd = popenargs[0]
#          error = subprocess.CalledProcessError(retcode, cmd)
#          error.output = output
#          raise error
#    return output


def run():
	mixtapes = Mixtape.objects.filter(approved=True)
	for mixtape in mixtapes:
           urls = []
	   if not mixtape.mixtape_zip:
             output = []
	     temproot = settings.TEMP_ROOT
             mixtape_zip = mixtape.fullAlbumName
             mixtaperoot = os.path.join(temproot, mixtape_zip)
	     #Check if it already exists, if so, delete it and start anew
             if os.path.isdir(mixtaperoot):
                print '\t--> Deleting existing directory with the same name!'
                shutil.rmtree(mixtaperoot)

             #Make the directory
             os.mkdir(mixtaperoot)
             print '\t--> New directory created'

             #Run this as a group in celery
             import requests
             output =[]
             count = 0
             for t in mixtape.tracks.all():
              count = count + 1
              url = t.url
	      print t.url
	      if 'https' in url:
		      url = t.signed_url
		      
		      if 'http'  in url:
			filename = t.filename
			if filename.endswith('.mp3'):
			  filename = str(count)+'-'+str(filename)
			  #filename = filename.split('.')[0]+str(count)+'.'+filename.split('.')[-1]
			if '/' in filename:
			  filename = re.sub(r'/','-',filename)
			if ' ' in filename:
			  filename = re.sub(r' ','-',filename)
			filepath = os.path.join(mixtaperoot, filename)
			f = open(filepath, 'w+')
			r = requests.get(url=url)
			f.write(r.content)
			#print '\nDownloading... \t\t--> %s' % (t.name)
		
			f.close()
			#print '... ... ... done: --> %s' % (filepath)
		
			setattr(t, 'filepath', filepath)
			output.append(t)
	      else:
		      pass

             for t in mixtape.images.all():

              url = t.signed_url
              print url
	      if url.startswith('https://cdn.247mixtapes.com/'):
		     
		      filename = t.filename
		      filepath = os.path.join(mixtaperoot, filename)
	
		      r = requests.get(url=url)
		      #print '\nDownloading... \t\t--> %s' % (t.name)
		      f = open(filepath, 'w+')
		      f.write(r.content)
		      f.close()
		      #print '... ... ... done: --> %s' % (filepath)
		      setattr(t, 'filepath', filepath)
		      output.append(t)
		      print '... ... ... -SUCCESS!'
		     
		      #generating key for signedurl for downloading file from filepicker.io
		      calls = ['pick', 'store']
		      expiry = 60*60*24
		      polexp = int(time.time() + expiry)
		      json_policy = json.dumps({'expiry': polexp, 'call':calls})
		      
		      #generating policy
		      policy = base64.urlsafe_b64encode(json_policy)	     
		      secret = settings.FILEPICKER_APP_SECRET
		       
		      #generating signature
		      signature = hmac.new(secret, policy, hashlib.sha256).hexdigest()
		      
		      file=shutil.make_archive(mixtaperoot, "zip", mixtaperoot)
		      escapedname = '\"%s\"' % file.replace('"', '\\\\\\"')
		      #output = subprocess.check_output('curl --progress-bar -F "fileUpload=@%(filename)s" -F "apikey=%(apikey)s" %(fpurl)s/api/path/storage/%(fileurl)s' % {"filename": escapedname, "apikey": APIKEY, "fpurl": FPURL, "fileurl": urllib.pathname2url(file)},shell=True)
		      curl_url = 'curl  -X POST  -F  fileUpload=@%s  "https://www.filepicker.io/api/store/S3?key=%s&policy=%s&signature=%s"' %(escapedname,APIKEY,policy,signature)
		      output =subprocess.check_output(curl_url,shell=True)
	     
	     try:
		     
		
        	data = json.loads(output)
	        url = data['key']
		url_path = "%s" %(url)
	        url_aws_path = 'https://cdn.247mixtapes.com/%s' %(url_path)		
                #mixtape_zip_url = url.replace(FPURL,CDN_URL)
                mixtape.mixtape_zip = url_aws_path
                mixtape.save()
                shutil.rmtree(mixtaperoot)
                os.remove(file)
        	urls.append(url)
	     except (ValueError, IndexError):
        	print "***ERROR***"
	        print output
	   


