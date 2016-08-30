from __future__ import absolute_import
from django.conf import settings
from django.core.files import File
from django.core.mail import EmailMessage, send_mail
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.sites.models import get_current_site, Site
from Mixtapes.celery import app
import bitly_api as bitly
import requests, os, shutil, zipfile, glob
from mixtape.models import *
from tweets.models import get_bitly_api
from audiofield.models import AudioFile

#Chaining a group together with another task will automatically upgrade it to be a chord:


@app.task
def mkFolder(instance):
    #Make the directory
    #http://effbot.org/librarybook/zipfile.htm
    temproot = settings.TEMP_ROOT
    mixtaperoot = os.path.join(temproot, instance.fullAlbumName)
    os.mkdir(mixtaperoot)
    print '\t--> Creating temp folder!'

@app.task
def dlTrack(t):

    #t = the track instance

    temproot = settings.TEMP_ROOT
    mixtaperoot = os.path.join(temproot, t.mixtape.fullAlbumName)
    
    url = t.secure_url
    filename = t.ordered_filename
    filepath = os.path.join(mixtaperoot, filename)
    r = requests.get(url=url)
    print '\nDownloading... \t\t--> %s' % (t.name)
    f = open(filepath, 'w+')
    f.write(r.content)
    f.close()
    print '... ... ... done: --> %s' % (filepath)

    setattr(t, 'filepath', filepath)
    return t

@app.task
def dlCover(mixtape):
    #mixtape is mixtape instance
    temproot = settings.TEMP_ROOT
    mixtaperoot = os.path.join(temproot, mixtape.fullAlbumName)

    #Download Cover Image
    r = requests.get(url=mixtape.album_cover)
    print '\nDownloading cover image!'
    filepath = os.path.join(mixtaperoot, 'cover.jpg')
    f = open(filepath, 'w+')
    f.write(r.content)
    f.close()
    print '--> done!'
    return f

@app.task
def s3Zip(mt):
    #takes list of tracks and zips
    #http://effbot.org/librarybook/zipfile.htm

    temproot = settings.TEMP_ROOT
    mixtaperoot = os.path.join(temproot, mt.fullAlbumName)

    fullpath = os.path.join(mixtaperoot, '%s_FULL' % (mt.fullAlbumName))

    file = zipfile.ZipFile(fullpath, 'w')

    for t in mt.mixtape_tracks.all():
        filepath = os.path.join(mixtaperoot, t.ordered_filename)
        file.write(filepath, t.ordered_filename, zipfile.ZIP_DEFLATED)

    try:
        coverpath = os.path.join(mixtaperoot, 'cover.jpg')
        file.write(coverpath, 'cover.jpg', zipfile.ZIP_DEFLATED)
    except:
        print 'No album cover!'

    file.close()
    print '\t--> %s - full album zip created!' % (mt.title)

@app.task
def s3Upload(instance):
    #Takes a mixtape instance
    temproot = settings.TEMP_ROOT
    mixtaperoot = os.path.join(temproot, instance.fullAlbumName)
    fullpath = os.path.join(mixtaperoot, '%s_FULL' % (instance.fullAlbumName))
    fa = File(open(fullpath))

    entry = FullAlbumAmazon.objects.filter(mixtape__id=instance.id)
    if entry.exists():
        entry.delete()
        print 'Overwriting existing entry in S3, and deleting old entry in the db!'
    else:
        print 'Creating new entry in S3!'

    aws = FullAlbumAmazon(mixtape=instance, archive=fa)
    aws.save()
    print 'SUCCESS! \t\t--> %s uploaded to S3!' % instance.title
    if settings.DEBUG and settings.ON_LOCAL:
        print '\t\t==> ACTUALLY... JUST UPLOADED TO YOUR LOCAL MEDIA SINCE YOU ARE ON LOCAL'
    return aws

@app.task
def fpUpload(instance):
    to_url = '%s/%s?key=%s' % (settings.FILEPICKER_STORE_API, 'S3', settings.FILEPICKER_API_KEY)
    r = requests.post(to_url, data=instance.payload)
    if r.status_code == 200:
        print '\t\t==>Uploaded full album to FP!'
        from .models import FullAlbum
        import ujson as json
        data = json.loads(r.text)
        fa = FullAlbum(
                mixtape=instance.mixtape,
                url=data['url'],
                filename='%s.zip' % instance.mixtape.slug,
                size=data['size'],
                awskey=data['key']
            )
        fa.save()
        if fa.pk:
            print '\t\t==>Saved full album as model'
            
@app.task            
def scUpload(mixtape):
    from .models import Track
    #import pdb;pdb.set_trace()
    temproot = settings.TEMP_ROOT
    mixtaperoot = os.path.join(temproot, mixtape.fullAlbumName)                
    alltracks = Track.objects.filter(mixtape = mixtape)
    client = getClient()
    import soundcloud
    import requests
    if os.path.isdir(mixtaperoot):
        print '\t--> Deleting existing directory with the same name!'
        shutil.rmtree(mixtaperoot)


    #Make the directory
    os.mkdir(mixtaperoot)
    print '\t--> New directory created'
    track_ids =[]
   
    #new change for mixtape drop sample track save
    try:
        audio=AudioFile.objects.filter(sample_track=True)[0]
        filename = slugify(audio.name)
        if audio.has_soundcloud():
            souncloud_id = audio.has_soundcloud()
        else:
            filepath = os.path.join(mixtaperoot, filename)
            filename = '24/7Mixtapes Drop'
            url = audio.audio_file.url.replace('/media/',settings.MEDIA_URL)
            r = requests.get(url=url)
            f = open(filepath, 'w+')
            f.write(r.content)
            f.close()
            print r
            print '\nDownloading... \t\t--> %s' % (filename)
            #f = open(filepath, 'w+')
            #f.write(r.content)
            sct = client.post('/tracks', track={
                'title': filename,
                'sharing': 'private',
                'asset_data': open(filepath, 'rb')
            })
            from mixtape.models import MixtapeSampleDrop
            mixtape_sample_obj = MixtapeSampleDrop(audio_sample=audio)
            mixtape_sample_obj.save()
            mixtape_sample_obj.soundcloud_sample_id = int(sct.id)
            mixtape_sample_obj.soundcloud_sample_uri = sct.uri
            print 'track uri: %s' % sct.uri
            mixtape_sample_obj.soundcloud_sample_permalink = sct.permalink_url
            mixtape_sample_obj.save()
            souncloud_id = mixtape_sample_obj.soundcloud_sample_id

    except:
        pass
        ##audio = ''
        ##filename = slugify('24/7Mixtapes Drop')
        
        ## create the playlist
      
    for t in mixtape.tracks.all():
        
        print t.url
        
        url = t.url
        
        if 'https' in url:
                url = t.signed_url
                filename = slugify(t.filename)
                filepath = os.path.join(mixtaperoot, filename)
                r = requests.get(url=url)
                f = open(filepath, 'w+')
                f.write(r.content)
                f.close()
                print r
                print '\nDownloading... \t\t--> %s' % (t.name)
                #f = open(filepath, 'w+')
                #f.write(r.content)
                sct = client.post('/tracks', track={
                    'title': filename,
                    'sharing': 'private',
                    'asset_data': open(filepath, 'rb')
                })
                t.soundcloud_id = int(sct.id)
                print 'track id: %s' % sct.id
                track_ids.append(int(sct.id))
        
                t.soundcloud_uri = sct.uri
                print 'track uri: %s' % sct.uri
        
                t.soundcloud_permalink = sct.permalink_url
                print 'track permalink: %s' % sct.permalink_url
        
                t.save()

    # print track link
   # print sct.permalink_url

    image = mixtape.mixtape_list_image()
    filename = 'cover.jpg'
    filepath = os.path.join(mixtaperoot, filename)
    r = requests.get(url=image)
    #print '\nDownloading... \t\t--> %s' % (t.name)
    f = open(filepath, 'w+')
    f.write(r.content)
    f.close()
    tracks_list = mixtape.tracks.values_list('soundcloud_id', flat=True)
    tracks_count = filter(None,tracks_list)
    
    if len(tracks_count) > 2:
        tracks_count.insert(2,souncloud_id)
    else:
        tracks_count.append(souncloud_id)
        
    tracks = map(lambda id: dict(id=id),tracks_count)
    # create the playlist
    
    playlist = client.post('/playlists', playlist={
        'title': mixtape.name,
        'sharing': 'private',
        "downloadable": "false",
        "embeddable_by": "me",
        'tracks': tracks
    })
    
    mixtape.soundcloud_id = playlist.id
    bitly = get_bitly_api()
    url = bitly.shorten('https://w.soundcloud.com/player/?url=%s&auto_play=false&show_artwork=true&sharing=false&show_user=true&show_comments=true&visual=false' %(playlist.secret_uri))['url']
    mixtape.soundcloud_uri = url
    mixtape.soundcloud_permalink = playlist.permalink_url
    #mixtape.save(dontruntasks=True)
    client.put(playlist.uri, playlist={
                'genre':mixtape.primaryGenre.name,
                'artwork_data':open(os.path.join(mixtaperoot, 'cover.jpg'), 'rb'),
                'downloadable':False
                })    

    print '%s \t--> SUCCESS!' % (mixtape.name)    

@app.task
def scTrackUpload(track, client):
    temproot = settings.TEMP_ROOT
    mixtaperoot = os.path.join(temproot, track.mixtape.fullAlbumName)
    #Takes a track instance
    print 'STARTING UPLOAD: %s' % track.name
    try:
        sct = client.post('/tracks',
            track={
                'title':track.name,
                'asset_data':open(os.path.join(mixtaperoot, track.ordered_filename), 'rb')        }
        )
        track.soundcloud_id = int(sct.id)
        print 'track id: %s' % sct.id

        track.soundcloud_uri = sct.uri
        print 'track uri: %s' % sct.uri

        track.soundcloud_permalink = sct.permalink_url
        print 'track permalink: %s' % sct.permalink_url

        track.save()

        print '%s \t--> SUCCESS!\n' % (track.name)

        client.put(sct.uri, track={
            'sharing':'public',
            'downloadable':False
            })
        print '\t\t--> Meta data changed!\n'
        #return sct
    except Exception,e:
        print '--> UPLOAD FAILED!',e


@app.task
def scMakePlaylist(instance, client):
    #Takes a mixtape instance
    temproot = settings.TEMP_ROOT
    mixtaperoot = os.path.join(temproot, instance.fullAlbumName)

    try:
        # create an array of track ids
        tracks = map(lambda id: dict(id=id), instance.mixtape_tracks.values_list('soundcloud_id', flat=True))

        mixtape = instance

        print 'CREATING PLAYLIST: %s' % mixtape.title

        playlist = client.post('/playlists', playlist={
            'title':mixtape.title,
            'tracks':tracks,
            'sharing':'public'
            })

        mixtape.soundcloud_id = playlist.id
        mixtape.soundcloud_uri = playlist.uri
        mixtape.soundcloud_permalink = playlist.permalink_url
        mixtape.save(dontruntasks=True)

        print '%s \t--> SUCCESS!' % (mixtape.title)

        client.put(playlist.uri, playlist={
            'genre':mixtape.primaryGenre.title,
            'artwork_data':open(os.path.join(mixtaperoot, 'cover.jpg'), 'rb'),
            'downloadable':False
            })
        print '\t\t--> Meta data changed!\n'
    except:
        print '--> could NOT make playlist in SC!'

        print '\n\n~~~~~~~~~~~~~~~~~~~~ALL DONE!~~~~~~~~~~~~~~~~~~~~\n\n'

@app.task
def cleanFiles(instance):
    #http://effbot.org/librarybook/zipfile.htm
    temproot = settings.TEMP_ROOT
    mixtaperoot = os.path.join(temproot, instance.fullAlbumName)

    #Check if it already exists, if so, delete it and start anew
    if os.path.isdir(mixtaperoot):
        print '\t--> Cleaning up folder!'
        shutil.rmtree(mixtaperoot)

@app.task
def mkFolder(instance):
    #Make the directory
    #http://effbot.org/librarybook/zipfile.htm
    temproot = settings.TEMP_ROOT
    mixtaperoot = os.path.join(temproot, instance.fullAlbumName)
    os.mkdir(mixtaperoot)
    print '\t--> Creating temp folder!'

@app.task
def scDelPlaylist(instance, client):
    playlistid = instance.soundcloud_id
    try:
        #Delete playlist
        client.delete('/playlists/%s' % playlistid)
        print '\t\t--> Playlist deleted!'
    except:
        pass
        print '\t\t ======> No playlist found!'

@app.task
def scDelTrack(track, client):
    trackid = track.soundcloud_id

    #Delete tracks
    try:
        client.delete('/tracks/%s' % trackid)
        print '\t\t--> Track deleted!'

    except:
        print '\t\t ======> No Track found!'


@app.task
def sendAdminApprovedEmail(mt):

    currentsite = Site.objects.get_current().domain

    print 'SENDING APPROVAL EMAIL'
    send_mail(
        'Mixtape Approved - %s' % mt.name,

        '''Congratulations!\n
        Your mixtape, %s, has been approved!\n
        Your mixtape can be viewed at: http://%s%s\n
        Editing is allowed within the first 48 hours of release, but your mixtape will need to be re-approved before being released once again. After 48 hours, no more editing of mixtapes will be allowed without admin approval.'''
        % (mt.name, currentsite, mt.get_absolute_url()),

        'support@247mixtapes.com',
        [mt.created_by.email]
        )
    print '\t\t ======> done!'




@app.task
def send_delayed_approval_email(**kwargs):
    EmailMessage(**kwagrs).send()
    
@app.task
def sendNotifyAdminEmail(mt):

        print 'SENDING ADMIN NOTIFICATION EMAIL'
        currentsite = Site.objects.get_current().domain
        send_mail(
                'Approval Request - %s' % mt.name,
                'Please review this mixtape: http://%s%s' % (currentsite, reverse('admin:mixtape_mixtape_change', args=(mt.id,))),
                'notify@247mixtapes.com',
                settings.ADMINS
                )
        print '\t\t ======> done!'

from mixtape import utils

@app.task
def soundcloud_upload(mixtape):
    utils.sc_upload_mixtape(mixtape)

@app.task
def mixtape_zip_upload(mixtape):
    utils.filepicker_upload_mixtape_zip(mixtape)
