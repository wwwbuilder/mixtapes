"""
Soundcloud upload
"""

def download_track(track):
    import requests
    import os
    import shutil
    from django.conf import settings
    from django.template.defaultfilters import slugify
    from django.utils.http import urlquote
    from inkblob.utils import get_signed_url
    temproot = settings.TEMP_ROOT
    mixtaperoot = os.path.join(temproot, track.mixtape.fullAlbumName)
    #Check if it already exists, if so, delete it and start anew
    if os.path.isdir(mixtaperoot):
        shutil.rmtree(mixtaperoot)
    #Make the directory
    os.mkdir(mixtaperoot)
    filename = '%s_%s' % (track.display_order, track.filename)
    filename = slugify(filename)
    filetype = track.filename.split('.')[-1]
    filepath = os.path.join(mixtaperoot, '%s.%s') % (filename, filetype)
    print '\nDownloading... \t\t--> %s' % (track.name)
    url = urlquote(track.aws_url, safe=':/?=&~')
    url = get_signed_url(url, url, 180)
    print url
    r = requests.get(url=url)
    f = open(filepath, 'w+')
    f.write(r.content)
    f.close()
    print '... ... ... done: --> %s' % (filepath)
    print 'size: '+str(os.path.getsize(filepath))
    return filepath

def sc_get_client():
    from mixtape.models import SoundCloudInfo
    from soundcloud import Client
    from django.conf import settings
    data = SoundCloudInfo.objects.filter(active = True)
    if data:
        data = data[0]
        creds = {
        'client_id': data.client_id,
        'client_secret':data.client_secret,
        'username':data.username, 
        'password':data.password,
        }
        return Client(**creds)
    else:
        return None

def sc_upload_track(track):
    print 'Soundcloud upload: track "%s"' % (track.filename)    
    sc = sc_get_client()
    # if already has soundcloud uri: return its sc object
    if track.soundcloud_uri:
        try:
            sct = sc.get(track.soundcloud_uri)
            print('Track already in soundcloud')
            return sct
        except: pass
    # if no sc uri or inaccessible: upload
    sct = sc.post('/tracks',
        track={
            'title':track.filename,
            #'artwork_url':track.album_cover,
            'asset_data':open(download_track(track), 'rb',),
            'sharing':'private',
            'track_type':'Remix',
            'downloadable':False,
        }
    )
    track.soundcloud_id = sct.id
    track.soundcloud_uri = sct.uri
    track.soundcloud_permalink = sct.permalink_url + '/' + sc.get(sct.uri).secret_token
    track.save()
    print('Track uploaded')
    return sct

def sc_get_mtdrop_track():
    sc = sc_get_client()
    # try finding it under 'mtdrop' name among current sc account tracks
    mtdrop_url = 'https://soundcloud.com/' + sc.get('/me').permalink + '/mtdrop'
    try: mtdrop = sc.get('resolve', url=mtdrop_url)
    except:
        # if not available, upload
        filepath = os.path.join(settings.TEMP_ROOT, '247Mixtapes.mp3')
        f = open(filepath, 'w+')
        import requests
        f.write(requests.get(url='https://static.247mixtapes.com/upload/audiofiles/247Mixtapes.mp3').content)
        f.close()
        mtdrop = sc.post('/tracks',
            track={
                'title':'mtdrop',
                'asset_data':open(filepath, 'rb',),
                'sharing':'public'
            }
        )
    return mtdrop

def sc_create_playlist(mixtape):
    sc = sc_get_client()
    # construct a dict for sc playlist
    tracks = []
    for track in mixtape.tracks.all():
        tracks += [{'id': sc_upload_track(track).id}]
    # insert the drop track as a 3rd track in every playlist
    tracks.insert(2, {'id': sc_get_mtdrop_track().id})
    playlist_dict = {
            'title': mixtape.name,
            'tracks': tracks,
            'sharing':'private',
            'genre': mixtape.primaryGenre.name,
            #'artwork_url': mixtape.album_cover,
            'downloadable': False,
    }
    # if already has soundcloud uri: update
    if mixtape.soundcloud_uri:
        try:
            #playlist = client.get(mixtape.soundcloud_uri)
            playlist = sc.put(mixtape.soundcloud_uri, playlist=playlist_dict)
            print('Playlist already in soundcloud, updated')
            return playlist
        except: pass
    # if no soundcloud uri or inaccessible: create
    playlist = sc.post('/playlists', playlist=playlist_dict)
    mixtape.soundcloud_id = playlist.id 
    mixtape.soundcloud_uri = playlist.uri 
    mixtape.soundcloud_permalink = playlist.permalink_url + '/' + sc.get(playlist.uri).secret_token
    mixtape.save()
    print('Playlist created')
    return playlist

def sc_upload_mixtape(mixtape):
    print 'Soundcloud upload: mixtape "%s"' % (mixtape.name)
    sc_create_playlist(mixtape)

"""
Mixtape zip upload
"""

def filepicker_upload_mixtape_zip(mixtape):

    import subprocess
    import os
    import shutil
    from django.conf import settings

    from subprocess import CalledProcessError

    import urllib
    import json
    import sys
    import os
    import ConfigParser
    import argparse
    import time
    import hmac, hashlib, time, base64
    import re

    #######################
    # Constants
    FPURL = "https://www.filepicker.io"
    CDN_URL = 'https://cdn.247mixtapes.com/'
    FPAPIURL = "https://developers.filepicker.io"
    CONFIG_FILE = os.path.expanduser('~/.geturl')

    #######################
    # Loading Config
    APIKEY = settings.FILEPICKER_API_KEY

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
        curl_output =subprocess.check_output(curl_url,shell=True)

        try:
            print curl_output
            data = json.loads(curl_output)
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
            print curl_output
