import os, re
import shutil, zipfile
from django.utils import timezone
from dateutil.relativedelta import *
from decimal import *
from datetime import datetime
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.template.loader import get_template
from django.template import Context, Template
from django.db import models
from django.db.models.signals import *
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse_lazy, reverse
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from django.contrib.sites.models import get_current_site, Site
from _base.models import BaseClass, GenericFKBaseClass
from _base.mixins import GenericFKMixin
from inkblob.models import InkBlob
from inkblob.utils import getpolicy, getsignature ,get_signed_url
from .sc import getClient
from celery import chord, group
import mandrill
#from .tasks import *
#from .tasks import send_delayed_approval_email
from mixtape import tasks
from .managers import *
from tweets.models import Tweet
from cgi import escape
from django.core.mail import EmailMultiAlternatives

import pytz


from audiofield.models import AudioFile
from django.conf import settings
import os.path

import logging
logger = logging.getLogger(__name__)

from embed_video.fields import EmbedVideoField

class AddonCategory(BaseClass):
    pass

    class Meta:
        verbose_name = _('Addon Category')
        verbose_name_plural = _('Addon Categories')

    def __unicode__(self):
        return '%s' % self.name
    


class AddonType(BaseClass):
    category = models.ForeignKey('AddonCategory', blank=True, null=True, related_name='addontypes')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    duration = models.IntegerField(blank=True, null=True, help_text='Duration in days')

    class Meta(GenericFKBaseClass.Meta):
        verbose_name = _('Addon Type')
        verbose_name_plural = _('Addon Types')


class AddonCharge(GenericFKBaseClass):
    end_datetime = models.DateTimeField(blank=True, null=True)
    charge = models.ForeignKey('payments.Charge', related_name='addon_charges')
    addon = models.ForeignKey('AddonType')

    @classmethod
    def create_charge(cls, userobj, addonobj, mixtapeobj):
        cu = userobj.customer
        ao = addonobj
        mt = mixtapeobj
        char = cu.charge(amount=Decimal(ao.price), description=addonobj.name)
        print '%s charge created for %s' % (ao.name, userobj.username)
        if ao.duration:
            if not mt.releaseDatetime > datetime.now(pytz.utc):
                edt = datetime.now(pytz.utc) + relativedelta(days=ao.duration)
            else:
                if ao.name in ['Basic Mixtape Page Countdown', 'Enhanced Homepage Mixtape Countdown']:
                    edt = mt.releaseDatetime
                else:
                    edt = mt.releaseDatetime + relativedelta(days=ao.duration)
        else:
            edt = None
        ac = AddonCharge(
            end_datetime = edt,
            charge = char,
            addon = ao,
            content_type_id=mt.get_content_type_id(),
            object_id=mt.id,
            updated_by=userobj,
            created_by=userobj
            )
        ac.save()
        # mt.addons= ac
        # mt.save()

        tweet = AddonType.objects.get(name='Tweet Your Mixtape')
        
        #Create tweet if this is the tweet addon
        if ac.addon == tweet and ac.id:
            Tweet.maketweet(mixtapeobj)
        return ac

    @property
    def status(self):
        if self.end_date < datetime.now(pytz.utc):
            return 'expired'
        elif self.end_date > datetime.now(pytz.utc):
            return 'active'
    @property
    def mixtape(self):
        mixtape_obj = Mixtape.objects.get(id=self.object_id)
        return mixtape_obj

class Genre(BaseClass):

    class Meta(BaseClass.Meta):
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')

    def __unicode__(self):
        return ('%s') % self.name

    def get_absolute_url(self):
        if self.name == 'Rap':
            return reverse('rap_mixtapes')
        elif self.name == 'Blends':
            return reverse('blend_mixtapes')
        elif self.name == 'Reggae':
            return reverse('reggae_mixtapes')
        elif self.name == 'East Coast':
            return reverse('eastcoast_mixtapes')
        elif self.name == 'Dirty South':
            return reverse('dirtysouth_mixtapes')
        elif self.name == 'R&B':
            return reverse('rnb_mixtapes')
        elif self.name == 'Chopped & Screwed':
            return reverse('chopped_mixtapes')
        else:
            return reverse('instrumentals_mixtapes')

    # @property
    # def mixtape_listings_url(self):
    #     return reverse('genre_mixtape_list', kwargs={'genre':self.slug})

    # @property
    # def profile_listings_url(self):
    #     return reverse('genre_mixtape_list', kwargs={'genre':self.slug})

class Mixtape(BaseClass):
    primaryGenre = models.ForeignKey('mixtape.Genre', related_name='mixtape_primaryGenre', verbose_name='Genre')
    primaryArtist = models.ForeignKey('userprofile.UserProfile', related_name='mixtape_primaryArtist', verbose_name='Featured Artist')
    video_url = EmbedVideoField('Video URL', blank=True, help_text='We will feature this on the mixtape page')
    releaseDatetime = models.DateTimeField('Release Date & Time', blank=True, null=True, help_text='Future release? When does this mixtape drop?', default=datetime.now(pytz.utc))
    
    editable = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    
    images = generic.GenericRelation('_misc.Image')
    addons = generic.GenericRelation('AddonCharge')
    
    #Soundcloud Info
    soundcloud_id = models.IntegerField(max_length=100, blank=True, null=True)
    soundcloud_uri = models.URLField(blank=True)
    soundcloud_permalink = models.URLField(blank=True)
    soundcloud_playback_count = models.IntegerField(blank=True, null=True)
    soundcloud_favoritings_count = models.IntegerField(blank=True, null=True)
    soundcloud_comment_count = models.IntegerField(blank=True, null=True)
    use_soundcloud_player = models.BooleanField(default=True, blank=True)
    djs = models.ForeignKey('userprofile.UserProfile', blank=True, null=True, related_name='mixtape_djs')
    description = models.CharField(max_length=160,null=True, blank=True)
    producer = models.ForeignKey('userprofile.UserProfile', blank=True, null=True, related_name='mixtape_producer')
    secondaryArtist = models.ForeignKey('userprofile.UserProfile',blank=True, null=True, related_name='mixtape_secondaryArtist')
    #mixtapes = MixtapeManager()
    mixtape_zip = models.CharField(max_length=250,blank=True, null=True)

    class Meta(BaseClass.Meta):
        unique_together = ('primaryArtist', 'slug', 'created_by',)
        verbose_name = _('Mixtape')
        verbose_name_plural = _('Mixtapes')

    def full_mixtape_slug(self):
        return '%s---%s---%s' % (
            slugify(self.primaryArtist.username),
            slugify(self.name),
            slugify(getattr(self.created_by, 'username', 'anonymous'))
            )
    
    def tracksurl(self):
        return mark_safe('<a href="/admin/mixtape/track/?mixtape__id__exact=%d">Click to view tracks</a>' % (self.id))
    tracksurl.allow_tags = True
    tracksurl.short_description = "Tracks"
    
    def __init__(self, *args, **kwargs):
        #Keep a copy of the original values to see if this is a new approval
        #http://stackoverflow.com/a/1793323
        super(Mixtape, self).__init__(*args, **kwargs)
        self.__previously_approved = self.approved

    def __unicode__(self):
        return ('%s: %s') % (self.primaryArtist, self.name)        

    def save(self, *args, **kwargs):
        print args,kwargs
        currentsite = Site.objects.get_current().domain
        if self.releaseDatetime == None:
            self.releaseDatetime = datetime.now(pytz.utc)
        if self.pk is not None and self.approved == True:
            orig = Mixtape.objects.get(pk=self.pk)
            if orig.approved != self.approved:
                plaintext = get_template('mixtape/approve_email.txt')
		htmly     = get_template('mixtape/approve_email.html')
		d = Context({ 'email':self.created_by.email,'username':self.created_by ,'name':self.name,'site':currentsite,'url':self.get_absolute_url(),'id':self.id})
		#import pdb; pdb.set_trace()
		subject, from_email, to = 'Your Mixtape has been Approved', 'support@247mixtapes.com', self.created_by.email
		text_content = plaintext.render(d)
		html_content = htmly.render(d)
		msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
		msg.attach_alternative(html_content, "text/html")
		msg.send()

        # this seems to be the code which inserted drop track into every Mixtape, do we still need it?
        #        try:
        #            audio=AudioFile.objects.filter(sample_track=True)[0]
        #            audioslug = slugify(audio.name)
        #        except:
        #            audio = ''
        #            audioslug = ''
        #        if audio:
        #            print audio.name
        #            track_obj = Track(mixtape=self,url= settings.MEDIA_URL+str(audio.audio_file),filename=audioslug,order=3,)
        #            track_obj.save()
        #            if self.use_soundcloud_player == True:
        #                scUpload(self)

        # run external upload tasks if mixtape is approved and has tracks
        if self.approved and self.tracks.all():
            # only run upload tasks if uri fields are empty
            # this disables update after edit, but otherwise tasks are run on each save(), incl. stats updates, causing pointless requests to cloud servers
            # some tracks can be autoremoved in soundcloud for copyright violation, so this could have cause those tracks upload again and again
            if not self.soundcloud_uri:
                try: tasks.soundcloud_upload.delay(self)
                except Exception as e:
                    logger.error(e)
            if not self.mixtape_zip:
                try: tasks.mixtape_zip_upload.delay(self)
                except Exception as e:
                    logger.error(e)

        super(Mixtape, self).save(*args, **kwargs)


    @property
    def primaryArtist_slug(self):
        return slugify(self.primaryArtist.username)

    def mixtape_list_image(self):
        if self.images.exists():
            image = self.images.all()[0]
            if image:
                image_url = image.get_thumbnail()
                return image_url
        else:
                return 'https://placehold.it/100x100&text=No+Image!'

    @property
    def fullAlbumName(self):
        fullalbum = '%s_%s' % (self.primaryArtist_slug, self.slug)
        return fullalbum

    def send_approval_email(self, domain):
        data = {}
        data['subject'] = 'Approval Request - %s ft %s by %s' % (self.name, self.primaryArtist.username, self.created_by)
        data['body'] = '%s has requested approval for a mixtape: %s featuring %s\n\n%s%s' % (
            self.created_by, self.name, self.primaryArtist.username, 
            domain, reverse('admin:mixtape_mixtape_change', args=(self.id,))
            )
        data['from_email'] = 'The Servers <approval@247mixtapes.com>'
        data['to'] = User.objects.filter(is_superuser=True).values_list('email', flat=True)
        EmailMessage(**data).send()

    def mixtape_image(self):
        image = self.images.all()[0]
        if image:
            image_url = image.get_image()
            return image_url
        
    def get_mixtape_thumnail(self):
		if self.images.exists():
			image = self.images.all()[0]
			if image:
				return image.default_url
		else:
			return 'https://placehold.it/290x206&text=No+Image!'
   
    def get_absolute_url(self):

        self.slug = slugify(self.name)
        artist = slugify(self.primaryArtist.username)


        return reverse('my-account:mixtape_detail', kwargs={'artist':artist,'slug':self.slug,'id':self.id})
        #return reverse('my-account:mixtape_detail', kwargs={'id':self.id})
        #return ('mixtape_detail/%s/%s/%s' %(self.primaryArtist.username,self.slug,self.created_by.username))

    # def save(self, *args, **kwargs):
    #     if self.approved and not self.__previously_approved:

    #         #Send this with the save method to prevent a recrusive, neverending loop on scMakePlaylist()
    #         dontruntasks = kwargs.pop('dontruntasks', None)

    #         if not dontruntasks:
    #             print 'Start %s' % self.title
    #             print '======================='

    #             temproot = settings.TEMP_ROOT
    #             mixtaperoot = os.path.join(temproot, self.fullAlbumName)
    #             alltracks = self.mixtape_tracks.all()
    #             client = getClient()

    #             #Clean folder --> Delete SC Uploads

    #                 #Download tracks -->
    #  Downfrom .models import *load cover image

    #                     #--> Zip album --> Upload to S3
    #                     #--> Upload to SC --> Make Playlist

    #                         #--> Clean Files

    #             #Preparing the massive chain

    #             thechain = (

    #                 #Prepare folder
    #                 cleanFiles.si(self) | mkFolder.si(self) |

    #                 #Prepare tracks

    #                     #Download tracks
    #                     (group(dlTrack.si(t) for t in alltracks) | dlCover.si(self)) |

    #                     #SoundCloud delete old Playlists and Tracks
    #                     (scDelPlaylist.si(self, client) | group((scDelTrack.si(t, client) for t in alltracks))) |

    #                 #Upload tracks

    #                     #Upload S3
    #                     s3Zip.si(self) | s3Upload.si(self) |

    #                     #Upload to FP and create FullAlbum Instance in DB
    #                     fpUpload.s() |

    #                     #Upload to SC
    #                     (group((scTrackUpload.si(t, client) for t in alltracks)) | scMakePlaylist.si(self, client)) |

    #                 #Send approved message to uploader
    #                 sendAdminApprovedEmail.si(self)

    #                 )()

    #     super(Mixtape, self).save(*args, **kwargs)

    #     def get_absolute_url(self):
    #         return reverse('mixtape_detail',from .models import * kwargs={'artist':self.primaryArtist.slug, 'slug':self.slug, 'uploader':self.created_by.userprofile.slug})

    def addons_url(self):
        #print reverse('addons_detail', kwargs={'artist':self.primaryArtist.user.username, 'slug':self.slug, 'uploader':self.created_by.username})
        return reverse('addons_detail', kwargs={'id':self.id})

    def __unicode__(self):
        return ('%s: %s') % (self.primaryArtist, self.name)

    #     @property
    #     def totalplaybacks(self):
    #         playbacks = cache.get('totalplaybacks-%s' % self.id)
    #         if playbacks:
    #             return playbacks
    #         else:
    #             return ''

    #             #Mixtape.update_sc_stats(self)
    #             #playbacks = cache.get('totalplaybacks-%s' % self.id)
    #             #return playbacks

    #     @property
    #     def totalfavoritings(self):
    #         favoritings = cache.get('totalfavoritings-%s' % self.id)
    #         if favoritings:
    #             return favoritings
    #         else:
    #             return ''

    #             #Mixtape.update_sc_stats(self)
    #             #favoritings = cache.get('totalfavoritings-%s' % self.id)
    #             #return favoritings

    #     @property
    #     def totalcomments(self):
    #         comments = cache.get('totalcomments-%s' % self.id)
    #         if comments:
    #             return comments
    #         else:
    #             return ''

    #             #Mixtape.update_sc_stats(self)
    #             #comments = cache.get('totalcomments-%s' % self.id)
    #             #return comments

    #     @property
    #     def isSponsored(self):
    #         sponsored = MixtapeAddon.objects.get(title__contains='Sponsor')
    #         charge = AddonCharge.objects.filter(mixtape=self, addon=sponsored)
    #         if charge:
    #             return True
    #         else:
    #             return False

    #     @property
    #     def artistother(self):
    #         artistother = cache.get('%s-%s-artistother' % (self.slug, self.id))
    #         if not artistother:
    #             artistother = Mixtape.objects.filter(primaryArtist=self.primaryArtist).exclude(slug=self.slug).order_by('-created')[:4]
    #             cache.set('%s-%s-artistother' % (self.slug, self.id), artistother, 60*60)
    #         return artistother

    @property
    def isReleased(self):
        '''
        If there is a specific releaseDateTime set, checks whether the current time is passed the specified release datetime
        '''
        if self.releaseDatetime != None:
			if datetime.now(pytz.utc) > self.releaseDatetime:
				return True
			else:
				return False
			
        else:
            return True
        
    def mixtape_album(self):
        tracks = self.track.all()
        zip_subdir = settings.TEMP_ROOT
        zip_filename = "%s.zip" % self.name
        s = StringIO.StringIO()
        zf = zipfile.ZipFile(s, "w")
        for track in tracks:
            fdir, fname = os.path.split(track.filename)
            zip_path = os.path.join(zip_subdir, fname)
            zf.write(fpath, zip_path)
        zf.close()
            

    @property
    def fullAlbumName(self):
    
        fullalbum = '%s_%s' % (self.primaryArtist_slug, self.slug)
        return fullalbum

    #     @property
    #     def isVisible(self):
    #         '''
    #         Checks whether mixtape is approved and isReleased()
    #         '''
    #         if self.approved and self.isReleased:
    #             return True
    #         else:
    #             return False

    #     @property
    #     def isHighlighted(self):
    #         hi = MixtapeAddon.objects.get(title__contains='Highlight')
    #         if hi in self.active_addons:
    #             return True
    #         else:
    #             return False

    #     @property
    #     def track_count(self):
    #         return Track.objects.filter(mixtape=self).count()

    #     @property
    #     def album_cover(self):
    #         try:
    #             cov = cache.get('albumcover-%s' % self.id)
    #             if cov:
    #                 return cov
    #             else:
    #                 img = self.images.all()[0]
    #                 cov = '%s/convert?w=800&h=600&fit=crop&policy=%s&signature=%s&format=jpg' % (img.cdn_url, img.read_policy, img.read_signature)
    #                 cache.set('albumcover-%s' % self.id, cov, 60*60)
    #                 return cov

    #         except:
    #             return 'http://placehold.it/800&text=No+Image!'

    #     @property
    #     def admin_album_cover(self):
    #         try:
    #             cov = cache.get('admin_albumcover-%s' % self.id)
    #             if cov:
    #                 return cov
    #             else:
    #                 img = self.images.all()[0]
    #                 cov = '%s/convert?w=150&policy=%s&signature=%s&format=jpg' % (img.cdn_url, img.read_policy, img.read_signature)
    #                 cache.set('admin_albumcover-%s' % self.id, cov, 60*60)
    #                 return cov

    #         except:
    #             return 'http://placehold.it/150&text=No+Image!'

    #     @property
    #     def other_album_cover(self):
    #         try:
    #             cov = cache.get('other_albumcover-%s' % self.id)
    #             if cov:
    #                 return cov
    #             else:
    #                 img = self.images.all()[0]
    #                 cov = '%s/convert?h=370&w=370&fit=crop&policy=%s&signature=%s&format=jpg' % (img.cdn_url, img.read_policy, img.read_signature)
    #                 cache.set('other_albumcover-%s' % self.id, cov, 60*60)
    #                 return cov

    #         except:
    #             return 'http://placehold.it/370&text=No+Image!'

    #     @property
    #     def scaled_album_cover(self):
    #         try:
    #             cov = cache.get('scaled_albumcover-%s' % self.id)
    #             if cov:
    #                 return cov
    #             else:
    #                 img = self.images.all()[0]
    #                 cov = '%s/convert?h=370&w=370&fit=crop&policy=%s&signature=%s&format=jpg' % (img.cdn_url, img.read_policy, img.read_signature)
    #                 cache.set('scaled_albumcover-%s' % self.id, cov, 60*60)
    #                 return cov

    #         except:
    #             return 'http://placehold.it/370&text=No+Image!'

    @property
    def slider_album_cover(self):
        img = self.images.all()
        if img:
	    #cov = '%s/convert?w=1920&h=500&fit=crop&policy=%s&signature=%s&format=jpg' % (img[0].cdn_url, getpolicy('read'), getsignature('read'))
	    #return cov
	    return img[0].default_url
        else:
            return 'https://placehold.it/1920x500&text=No+Image!'

    @property
    def coming_soon_mixtape_image(self):
        img = self.images.all()
        if img:
            #cov = '%s/convert?w=290&h=240&fit=crop&policy=%s&signature=%s&format=jpg' % (img[0].cdn_url, getpolicy('read'), getsignature('read'))
            #return cov
            return img[0].default_url
        else:
            return 'https://placehold.it/290x240&text=No+Image!'


    #     @property
    #     def cover_image(self):
    #         try:
    #             cov = self.images.all()[0].secure_url
    #             return cov
    #         except:
    #             return ''

    #     @property
    #     def genre_list(self):
    #         return ', '.join(x.title for x in self.genres.all())

    @property
    def active_addons(self):
        try:
            active_charges = self.addons.filter(Q(end_datetime__gt=datetime.now(pytz.utc)) | Q(end_datetime=None)).prefetch_related()
            active_addons = []
            for x in active_charges:
                addon = x.addon
                setattr(addon, 'end_date', x.end_datetime)
                active_addons.append(addon)
            return active_addons
        except:
            return ''

    #     @property
    #     def hasCountdown(self):
    #         cd = MixtapeAddon.objects.filter(title__contains='Countdown')
    #         if any(x in cd for x in self.active_addons):
    #             return True
    #         else:
    #             return False

    @property
    def can_edit(self):
	if self.editable == True or relativedelta(timezone.now(), self.created).days < 2:
	    return True
	else:
	    return False

    #     @property
    #     def primaryArtist_slug(self):
    #         return slugify(self.primaryArtist.username)

    #     @property
    #     def amazon_url(self):
    #         try:
    #             return self.s3_fullalbum.archive.url
    #         except:
    #             return ''

    #     @property
    #     def soundcloudTracks(self):
    #         return self.mixtape_tracks.values_list('soundcloud_id', flat=True)

    def is_featured(self):
        if self.addons.all():
            return True
        else:
            return False

    @classmethod
    def downloadTracks(cls, instance,request):
        output = []
        temproot = settings.TEMP_ROOT
        mixtaperoot = os.path.join(temproot, instance.fullAlbumName)
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
        for t in instance.tracks.all():
            count = count + 1
            url = t.signed_url
            print url
            if 'http' not in url:
                currentsite = get_current_site(request)
                url=currentsite.domain+url
            filename = t.filename
            if filename.endswith('.mp3'):
                filename = filename.split('.')[0]+str(count)+'.'+filename.split('.')[-1]
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
            
        for t in instance.images.all():
            
            url = t.signed_url
            print url
            if 'http' not in url:
                currentsite = get_current_site(request)
                url=currentsite.domain+url
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
        #Download Cover Image
        #r = requests.get(url=instance.album_cover)
        #print '\nDownloading cover image!'
        #filepath = os.path.join(mixtaperoot, 'cover.jpg')
        #f = open(filepath, 'w+')
        #f.write(r.content)
        #f.close()
    
        print '... ... ... -SUCCESS!'

        return output

    @property
    def download_url(self):
        if self.mixtape_zip:
            url_path = self.mixtape_zip
            secs = 180
	    signed_url = get_signed_url(url_path,url_path,secs)
        else:
            signed_url = ""
        return signed_url

    #     @classmethod
    #     def soundcloudUpload(cls, instance):
    #         #Tracklist is the output from the download tracks method...

    #         #During the upload, don't specify any complicated meta data.
    #         #Instead, PUT meta data separately afterward.

    #         output = []

    #         tracklist = instance.mixtape_tracks.order_by('order')
    #         temproot = settings.TEMP_ROOT
    #         mixtaperoot = os.path.join(temproot, instance.fullAlbumName)

    #         client = getClient()

    #         '''
    #         #Put the drop as the second track in every playlist
    #         mtdrop = client.get('/tracks/103376718')
    #         '''

    #         n = 1
    #         for track in tracklist:
    #             sct = client.post('/tracks',
    #                 track={
    #                     'title':track.title,
    #                     'artwork_data':open(os.path.join(mixtaperoot, 'cover.jpg'), 'rb',),
    #                     'asset_data':open(os.path.join(mixtaperoot, track.ordered_filename), 'rb',),
    #                     'sharing':'public'
    #                 }
    #             )

    #             track.soundcloud_id = int(sct.id)
    #             print 'track id: %s' % sct.id

    #             track.soundcloud_uri = sct.uri
    #             print 'track uri: %s' % sct.uri

    #             track.soundcloud_permalink = sct.permalink_url
    #             print 'track permalink: %s' % sct.permalink_url

    #             track.save()

    #             '''
    #             #In this second spot, put in the 247 mixtapes drop
    #             if n == 2:
    #                 output.append(mtdrop)
    #             '''

    #             output.append(sct)
    #             print '%s \t--> SUCCESS!\n' % (track.title)

    #             client.put(sct.uri, track={
    #                 'track_type':'Remix',
    #                 'sharing':'public',
    #                 'downloadable':False
    #                 })
    #             print '\t\t--> Meta data changed!\n'
    #             n+=1

    #         print '\n\n~~~~~~~~~~~~~~~~~~~~ALL DONE!~~~~~~~~~~~~~~~~~~~~\n\n'

    #         return output

    #     @classmethod
    #     def soundcloudMakePlaylist(cls, instance, do_save=True):
    #         sc = getClient()
    #         temproot = settings.TEMP_ROOT
    #         mixtaperoot = os.path.join(temproot, instance.fullAlbumName)
    #         mixtape = instance

    #         # create an array of track ids
    #         tracks = map(lambda id: dict(id=id), instance.mixtape_tracks.values_list('soundcloud_id', flat=True))

    #         playlist = sc.post('/playlists', playlist={
    #             'title':mixtape.title,
    #             'tracks':tracks,
    #             'sharing':'public'
    #             })

    #         mixtape.soundcloud_id = playlist.id
    #         mixtape.soundcloud_uri = playlist.uri
    #         mixtape.soundcloud_permalink = playlist.permalink_url

    #         if do_save:
    #             mixtape.save()

    #         print '%s \t--> SUCCESS!' % (mixtape.title)

    #         sc.put(playlist.uri, playlist={
    #             'genre':mixtape.primaryGenre.title,
    #             'artwork_data':open(os.path.join(mixtaperoot, 'cover.jpg'), 'rb',),
    #             'sharing':'public',
    #             'downloadable':False
    #             })
    #         print '\t\t--> Meta data changed!\n'

    #         print '\n\n~~~~~~~~~~~~~~~~~~~~ALL DONE!~~~~~~~~~~~~~~~~~~~~\n\n'

    #     @classmethod
    #     def soundcloudDeleteAll(cls, instance):
    #         playlistid = instance.soundcloud_id
    #         trackids = instance.soundcloudTracks

    #         sc = getClient()

    #         if playlistid:
    #             try:
    #                 #Delete playlist
    #                 sc.delete('/playlists/%s' % playlistid)
    #                 print '\t\t--> Playlist deleted!'
    #             except:
    #                 pass
    #                 print '\t\t ======> PLAYLIST ERROR!'

    #         if trackids:
    #             #Delete tracks
    #             for t in trackids:
    #                 try:
    #                     sc.delete('/tracks/%s' % t)
    #                     print '\t\t--> Track deleted!'

    #                 except:
    #                     print '\t\t ======> TRACK ERROR!'

    #     @classmethod
    #     def update_sc_stats(cls, instance):
    #         client = getClient()
    #         playlist = client.get('/playlists/%s' % instance.soundcloud_id)
    #         trackinfo = playlist.fields()['tracks']
    #         mttracks = instance.mixtape_tracks.all()

    #         mtplaybacks = 0
    #         mtfavoritings = 0
    #         mtcomments = 0

    #         for t in mttracks:

    #             for item in trackinfo:

    #                 if item['id'] == t.soundcloud_id:

    #                     pbc = item['playback_count']
    #                     t.soundcloud_playback_count = pbc
    #                     mtplaybacks += pbc

    #                     print '\nPlayback count: %s' % pbc
    #                     print '%s' % type(pbc)

    #                     fvc = item['favoritings_count']
    #                     t.soundcloud_favoritings_count = fvc
    #                     mtfavoritings += fvc

    #                     print '\nFavoritings count: %s' % fvc
    #                     print '%s' % type(fvc)

    #                     cmc = item['comment_count']
    #                     t.soundcloud_comment_count = cmc
    #                     mtcomments += cmc

    #                     print '\nComments count: %s' % cmc
    #                     print '%s' % type(cmc)

    #                     t.save()
    #                     print '\n%s - updated!\n' % item['title']

    #         instance.soundcloud_playback_count = mtplaybacks
    #         cache.set('totalplaybacks-%s' % instance.id, mtplaybacks, 60*60)

    #         instance.soundcloud_favoritings_count = mtfavoritings
    #         cache.set('totalfavoritings-%s' % instance.id, mtfavoritings, 60*60)

    #         instance.soundcloud_comment_count = mtcomments
    #         cache.set('totalcomments-%s' % instance.id, mtcomments, 60*60)

    #         instance.save()

    #         print '%s - ALL UPDATED!\n' % instance.title

    #     @classmethod
    #     def fullalbum_zip(cls, instance):
    #         #http://effbot.org/librarybook/zipfile.htm
    #         temproot = settings.TEMP_ROOT
    #         mixtaperoot = os.path.join(temproot, instance.fullAlbumName)

    #         fullpath = os.path.join(mixtaperoot, '%s_FULL' % (instance.fullAlbumName))

    #         file = zipfile.ZipFile(fullpath, 'w')

    #         for t in instance.mixtape_tracks.all():
    #             filepath = os.path.join(mixtaperoot, t.ordered_filename)
    #             file.write(filepath, t.ordered_filename, zipfile.ZIP_DEFLATED)

    #         try:
    #             coverpath = os.path.join(mixtaperoot, 'cover.jpg')
    #             file.write(coverpath, 'cover.jpg', zipfile.ZIP_DEFLATED)
    #         except:
    #             print 'No album cover!'

    #         file.close()
    #         print '\t--> %s - full album zip created!' % (instance.title)

    #     @classmethod
    #     def fullalbum_AmazonUpload(cls, instance):
    #         temproot = settings.TEMP_ROOT
    #         mixtaperoot = os.path.join(temproot, instance.fullAlbumName)
    #         fullpath = os.path.join(mixtaperoot, '%s_FULL' % (instance.fullAlbumName))
    #         fa = File(open(fullpath))

    #         entry = FullAlbumAmazon.objects.filter(mixtape__id=instance.id)
    #         if entry.exists():
    #             entry.delete()
    #             print 'Overwriting existing entry in S3, and deleting old entry in the db!'
    #         else:
    #             print 'Creating new entry in S3!'

    #         aws = FullAlbumAmazon(mixtape=instance, archive=fa)
    #         aws.save()
    #         print 'SUCCESS! \t\t--> %s uploaded to S3!' % instance.title

    #     @classmethod
    #     def cleanfiles(cls, instance):
    #         #http://effbot.org/librarybook/zipfile.htm
    #         temproot = settings.TEMP_ROOT
    #         mixtaperoot = os.path.join(temproot, instance.fullAlbumName)

    #         #Check if it already exists, if so, delete it and start anew
    #         if os.path.isdir(mixtaperoot):
    #             print '\t--> Cleaning up folder!'
    #             shutil.rmtree(mixtaperoot)

    #     @classmethod
    #     def delete_s3_files(cls, instance):
    #         conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    #         bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)

    #         print '\n\nSTARTING TO DELETE S3 FILES!!!'
    #         print '============================================'
    #         thefiles = bucket.list(prefix='%s' % instance.fullAlbumName)
    #         for k in thefiles:
    #             try:
    #                 bucket.delete_key(k.name)
    #                 print 'DELETED - %s\n' % k.name
    #             except:
    #                 print 'Already deleted? - %s' % k.name

    #         print '\t--> Done deleting S3 files!\n'


    # def tweet_if_needed(sender, instance, using, **kwargs):
    #     if instance.approved:
    #         if instance.tweets.filter(tweet_id=None).exists():
    #             tweet = Tweet.objects.filter(mixtape=instance).order_by('-created')[0]
    #             Tweet.tweetout(tweet)
    #     else:
    #         pass

    # def delete_s3_folder(sender, instance, using, **kwargs):
    #     Mixtape.delete_s3_files(instance)

    # def delete_sc_files(sender, instance, using, **kwargs):
    #     print '\n\nSTARTING TO DELETE SOUNDCLOUD FILES!!!'
    #     print '============================================'
    #     Mixtape.soundcloudDeleteAll(instance)
    #     print 'Soundcloud Files Deleted!'

    # def cache_mts(sender, instance, **kwargs):
    #     cache.set('mts', Mixtape.objects.prefetch_related())

    # pre_delete.connect(delete_sc_files, sender=Mixtape)
    # pre_delete.connect(delete_s3_folder, sender=Mixtape)
    # post_save.connect(tweet_if_needed, sender=Mixtape)
    # post_save.connect(cache_mts, sender=Mixtape)


    # def delete_s3_file(sender, instance, using, **kwargs):

    #     conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    #     bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)

    #     try:
    #         bucket.delete_key(instance.awskey)
    #         print 'DELETED - %s' % instance.title
    #     except:
    #         print 'Already deleted? - %s' % instance.title

    # pre_delete.connect(delete_s3_file, sender=Mixtape)

class SoundCloudInfo(models.Model):
    active = models.BooleanField(default = False)
    client_id = models.CharField(max_length=255,blank = True, null = True)
    client_secret = models.CharField(max_length=255,blank = True, null = False)
    username = models.CharField(max_length=255,blank = True, null = True)
    password = models.CharField(max_length=255,blank = True, null = True)



class Track(InkBlob):
    mixtape = models.ForeignKey('mixtape.Mixtape', related_name='tracks')
    genres = models.ManyToManyField('mixtape.Genre', blank=True, null=True, related_name='genre_tracks')
    artists = models.ManyToManyField('userprofile.UserProfile', blank=True, null=True, related_name='artist_tracks')
    producers = models.ManyToManyField('userprofile.UserProfile', blank=True, null=True, related_name='producer_tracks')
    djs = models.ManyToManyField('userprofile.UserProfile', blank=True, null=True, related_name='dj_tracks')
    lyrics = models.TextField(blank=True)
    video_url = EmbedVideoField(blank=True)

    #Soundcloud Info
    soundcloud_id = models.IntegerField(blank=True, null=True)
    soundcloud_uri = models.URLField(blank=True)
    soundcloud_permalink = models.URLField(blank=True)
    soundcloud_playback_count = models.IntegerField(blank=True, null=True)
    soundcloud_favoritings_count = models.IntegerField(blank=True, null=True)
    soundcloud_comment_count = models.IntegerField(blank=True, null=True)

    class Meta(InkBlob.Meta):
        verbose_name = _('Track')
        verbose_name_plural = _('Tracks')
         

    @property
    def primaryArtist_slug(self):
        return self.mixtape.primaryArtist_slug        

    @property
    def ordered_filename(self):
        #Creates the name with the title, as opposed to the originally submitted filename
        return '%s_%s-%s.%s' % (self.display_order, self.primaryArtist_slug, self.slug, self.filename.split('.')[-1])                

    #     def other_genres(self):
    #         selectedGenres = self.genres.all().values_list('title', flat=True)
    #         return Genre.objects.exclude(title__in=selectedGenres).values('title', 'id')
    
    #     @property
    #     def album_cover(self):
    #         return self.mixtape.album_cover
    
    #     @property
    #     def display_order(self):
    #         try:
    #             return self.order + 1
    #         except:
    #             return 1

    @property
    def genre_list(self):
        return ', '.join(x.name for x in self.genres.all())

    @property
    def artist_list(self):
        return ', '.join(x.username for x in self.artists.all())

#     @property
#     def producer_list(self):
#         return ', '.join(x.username for x in self.producers.all())

#     @property
#     def dj_list(self):
#         return ', '.join(x.username for x in self.djs.all())

#     @property
#     def primaryArtist_slug(self):
#         return self.mixtape.primaryArtist_slug

#     @property
#     def ordered_filename(self):
#         #Creates the name with the title, as opposed to the originally submitted filename
#         return '%s_%s-%s.%s' % (self.display_order, self.primaryArtist_slug, self.slug, self.filename.split('.')[-1])

#     @property
#     def _genre(self):
#         try:
#             return self.genre.title
#         except:
#             return ''

# #pre_delete.connect(delete_s3_file, sender=Track)

class MixtapePageView(models.Model):
	date = models.DateTimeField(auto_now=True)
	mixtape = models.ForeignKey('mixtape.Mixtape', related_name='pageview')
    
    
class MixtapeFavorite(models.Model):
    user = models.ForeignKey('userprofile.UserProfile', related_name='mixtape_user')
    mixtape = models.ForeignKey('mixtape.Mixtape', related_name='mixtape')
    date = models.DateTimeField(auto_now=True)
		
class MixtapeSpotLight(models.Model):
	title = models.CharField(max_length=200, blank=True)
	artist = models.ForeignKey('userprofile.UserProfile', related_name='artist', verbose_name='Artist')
	image = models.ImageField(upload_to="spotlight/")
	created = models.DateTimeField(auto_now=True)
	description = models.TextField(blank=True)
    
class MixtapeDownloadLimit(models.Model):
    user = models.CharField(max_length=200, blank=True)
    date = models.DateField(auto_now=True)
    count = models.IntegerField(default=0)
    
class MixtapeSampleDrop(models.Model):
    audio_sample = models.ForeignKey(AudioFile)
    soundcloud_sample_id = models.IntegerField(max_length=100, blank=True, null=True)
    soundcloud_sample_uri = models.URLField(blank=True)
    soundcloud_sample_permalink = models.URLField(blank=True)    
    
class GoogleAdsBlock(models.Model):
    content = models.CharField( max_length=2000,blank=True,null=True)
    
    
    def __unicode__(self):
	    return '%s' % (self.content)    
