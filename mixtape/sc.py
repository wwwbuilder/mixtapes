def getClient():
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

def getTracks():
    sc = getClient()
    me = sc.get('/me')
    tracks = sc.get('/users/%s/tracks' % me.id)
    return tracks

def downloadTracks(mixtape):
    import requests
    import os
    import shutil
    from django.conf import settings
    from django.template.defaultfilters import slugify
    from django.utils.http import urlquote
    from inkblob.utils import get_signed_url
    output = []
    temproot = settings.TEMP_ROOT
    print mixtape
    mixtaperoot = os.path.join(temproot, mixtape.fullAlbumName)
    #Check if it already exists, if so, delete it and start anew
    if os.path.isdir(mixtaperoot):
        shutil.rmtree(mixtaperoot)
    #Make the directory
    os.mkdir(mixtaperoot)
    for t in mixtape.tracks.all():
        filename = '%s_%s' % (t.display_order, t.filename)
        filename = slugify(filename)
        filetype = t.filename.split('.')[-1]
        filepath = os.path.join(mixtaperoot, '%s.%s') % (filename, filetype)
        print '\nDownloading... \t\t--> %s' % (t.name)
        url = urlquote(t.aws_url, safe=':/?=&~')
        url = get_signed_url(url, url, 180)
        print url
        r = requests.get(url=url)
        f = open(filepath, 'w+')
        f.write(r.content)
        f.close()
        print '... ... ... done: --> %s' % (filepath)
        print 'size: '+str(os.path.getsize(filepath))
        setattr(t, 'filepath', filepath)
        output.append(t)
    return output

def uploadTracks(tracklist):
    #During the upload, don't specify any complicated meta data. 
    #Instead, PUT meta data separately afterward.
    #from .sc import getClient
    output = []
    client = getClient()
    #Put the drop as the second track in every playlist
    #mtdrop = client.get('/tracks/103376718')
    n = 1
    for track in tracklist:
        sct = client.post('/tracks',
            track={
                'title':track.filename,
                #'artwork_url':track.album_cover,
                'asset_data':open(track.filepath, 'rb',),
                'sharing':'private'
            }
        )
        track.soundcloud_id = sct.id 
        track.soundcloud_uri = sct.uri 
        track.soundcloud_permalink = sct.permalink_url
        track.save()
        #In this second spot, put in the 247 mixtapes drop
        #if n == 2:
        #    output.append(mtdrop)
        output.append(sct)
        print '%s \t--> SUCCESS!\n' % (track.name)    
        client.put(sct.uri, track={
            'track_type':'Remix',
            'sharing':'private',
            'downloadable':False
            })
        print '\t\t--> Meta data changed!\n'
        n+=1
        track.soundcloud_permalink = sct.permalink_url + '/' + client.get(sct.uri).secret_token
        track.save()
    print '\n\n~~~~~~~~~~~~~~~~~~~~ALL DONE!~~~~~~~~~~~~~~~~~~~~\n\n'
    return client, tracklist, output

def makePlaylist(mixtape, *output):
    #output refers to the tracklist with the drop mixed in from uploadTracks()
    #from .sc import getClient
    sc = getClient()
    tracks = map(lambda id: dict(id=id), [t.id for t in output])
    # insert the drop track as a 3rd track in every playlist
    mtdrop = getMtdrop()
    tracks.insert(2, {'id': mtdrop.id})
    playlist = sc.post('/playlists', playlist={
        'title':mixtape.name,
        'tracks':tracks,
        'sharing':'private'
        })
    mixtape.soundcloud_id = playlist.id 
    mixtape.soundcloud_uri = playlist.uri 
    mixtape.soundcloud_permalink = playlist.permalink_url
    mixtape.save()
    print '%s \t--> SUCCESS!' % (mixtape.name)    
    sc.put(playlist.uri, playlist={
        'genre':mixtape.primaryGenre.name,
        #'artwork_url':mixtape.album_cover,
        'sharing':'private',
        'downloadable':False
        })
    print '\t\t--> Meta data changed!\n'
    mixtape.soundcloud_permalink = playlist.permalink_url + '/' + sc.get(playlist.uri).secret_token
    mixtape.save()
    print '\n\n~~~~~~~~~~~~~~~~~~~~ALL DONE!~~~~~~~~~~~~~~~~~~~~\n\n'

def makePublic(mixtape):
    #from .sc import getClient
    sc = getClient()
    for track in mixtape.tracks.all():
        sc.put(track.soundcloud_uri, track={
            'sharing':'public'
            })
        print '%s --> DONE!' % (track.name)

def getMtdrop():
    sclient = getClient()
    mtdrop_url = 'https://soundcloud.com/' + sclient.get('/me').permalink + '/mtdrop'
    try: mtdrop = sclient.get('resolve', url=mtdrop_url)
    except:
        # upload mtdrop
        filepath = os.path.join(settings.TEMP_ROOT, '247Mixtapes.mp3')
        f = open(filepath, 'w+')
        import requests
        f.write(requests.get(url='http://static.247mixtapes.com/upload/audiofiles/247Mixtapes.mp3').content)
        f.close()
        mtdrop = sclient.post('/tracks',
            track={
                'title':'mtdrop',
                'asset_data':open(filepath, 'rb',),
                'sharing':'public'
            }
        )
    return mtdrop

def soundcloudSend(mixtape):
    #from core.sc import downloadTracks, uploadTracks, makePlaylist, makePublic
    tl = downloadTracks(mixtape)
    client, tracklist, output = uploadTracks(tl)
    makePlaylist(mixtape, *output)
    #makePublic(mixtape)
    print 'Uploaded to soundcloud -%s' % (mixtape.name)
