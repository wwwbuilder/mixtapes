from django.conf import settings
from inkblob.utils import getpolicy, getsignature
from mixtape.models import *
from userprofile.models import UserProfile
from analytics.models import Analytics
#from addon.models import *
def filepicker(request):
    # return the value you want as a dictionary. you may add multiple values in there.
    return {
        'FILEPICKER_API_KEY': settings.FILEPICKER_API_KEY,
        'FILEPICKER_UPLOAD_POLICY': getpolicy('upload'),
        'FILEPICKER_UPLOAD_SIGNATURE': getsignature('upload'),
        'FILEPICKER_READ_POLICY': getpolicy('read'),
        'FILEPICKER_READ_SIGNATURE': getsignature('read'),
        'FILEPICKER_DELETE_POLICY': getpolicy('delete'),
        'FILEPICKER_DELETE_SIGNATURE': getsignature('delete'),
        'genres':Genre.objects.all(),
        'artists':UserProfile.objects.all()
    }

def stripe(request):
    return {
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLIC_KEY
    }

def tracking_code(request):
    try:
        dict ={ 'TRACKING_CODE': Analytics.objects.all()[0].tracking_code}
    except:
        dict = {}
    
    return dict

def sitewide_slider(request):
    try:
        sadd = AddonType.objects.get(name__iexact='Sitewide Slider Upgrade',duration='7')
    except Exception,e:
        print e
    allslider = AddonCharge.objects.prefetch_related().filter(
        addon=sadd,
        end_datetime__gt=datetime.now(pytz.utc),
        mixtape__approved=True,
        mixtape__releaseDatetime__lt=datetime.now(pytz.utc)
        )

    #print '\n\nLENGTH OF ALLSLIDER IS %s' % len(allslider)
    print "allslider",allslider
    #Get the related mixtape objects
    if allslider:
        slider = [s.mixtape for s in allslider]
        print slider

    #If there are no mixtapes with this add-on... select a random up to 5
    else:
        slider = Mixtape.objects.filter(approved=True, releaseDatetime__lt=datetime.now(pytz.utc)).order_by('?')[:5]

    if len(slider) > 5:
        slider = random.sample(slider, 5)

    #print '\n\n\n\nTHERE ARE %s THINGS IN THE SLIDER!!!\n\n\n\n' % (len(slider))

    #cache.set('fp-slider', slider, 60*15)
    return {'slider':slider}