from django.template import Library
from datetime import datetime, timedelta
from django import template
import pytz
from mixtape.models import Mixtape, Genre, Track, AddonType, AddonCharge
from django.conf import settings
from inkblob.utils import get_signed_url

register = Library()


#template tag for converting static media urls to signed url

class S3StaticURL(template.Node):
    def __init__(self, static, path, as_var=None):
        self.static = static
        self.path = template.Variable(path)
        self.as_var = as_var

    def render(self, context):
        #import pdb;pdb.set_trace()
        path = self.path.resolve(context)
        if self.static:
            #base_url = settings.STATIC_URL
            base_url = 'http://static.247mixtapes.com/%s' %(path)
        else:
            #base_url = settings.MEDIA_URL
            base_url = 'http://static.247mixtapes.com/%s' %(path)

        secs = 180       
        url = get_signed_url(base_url,base_url,secs)
        
        if self.as_var:
            context[self.as_var] = url
            return ''
        else:
            return url


def do_s3_static_url(parser, token, static=False):
    """
    Usage::
        {% s3_static_url path %}
  
    """
    split_token = token.split_contents()
    vars = []
    as_var = False
    for k, v in enumerate(split_token[1:]):
        if v == 'as':
            try:
                while len(vars) < 1:
                    vars.append(None)
                vars.append(split_token[k+2])
                as_var = True
            except IndexError:
                raise template.TemplateSyntaxError(
                      "%r tag requires a variable name to attach to" \
                      % split_token[0]
                )
            break
        else:
            vars.append(v)

    if (not as_var and len(vars) not in (1,)) \
       or (as_var and len(vars) not in (2,)):
        raise template.TemplateSyntaxError(
              "%r tag requires a path or url" \
              % token.contents.split()[0]
        )

    return S3StaticURL(static, *vars)


do_s3_static_url = register.tag('s3_static_url', do_s3_static_url)




@register.filter()
def upfirstletter(value):
    first = value[0] if len(value) > 0 else ''
    remaining = value[1:] if len(value) > 1 else ''
    return first.upper() + remaining


@register.filter
def get_range(value):
    rating = int(value)
    return range(rating)

@register.filter
def get_offstar_range(value):
    rating = 5 - int(value)
    return range(rating)

@register.filter
def date_check(value):
    now = datetime.now()
    value=value.split('-')
    value=map(int, value)
    releaseDate = datetime(value[0],value[1],value[2],value[3],value[4],value[5])
    counterstart = releaseDate- timedelta(days=7)
    if releaseDate >= now and now >= counterstart:
        return True
    else:
        return False

@register.filter
def counter_value(value):
    
    now = datetime.now()
    value=value.split('-')
    value=map(int, value)
    releaseDate = datetime(value[0],value[1],value[2],value[3],value[4],value[5])
    counterstart = releaseDate- timedelta(days=7)
    counter = 0
    print "now:",now
    print "counterstart:",counterstart
    print "release:",releaseDate
    if releaseDate >= now and now >= counterstart:
        counter = releaseDate-now
        print counter
        counter = counter.total_seconds()
        print counter
    return counter



@register.filter
def date_check_home(value):
    now = datetime.now()
    value=value.split('-')
    value=map(int, value)
    releaseDate = datetime(value[0],value[1],value[2],value[3],value[4],value[5])
    counterstart = releaseDate- timedelta(days=1)
    if releaseDate >= now and now >= counterstart:
        return True
    else:
        return False

@register.filter
def counter_value_home(value):
    
    now = datetime.now()
    value=value.split('-')
    value=map(int, value)
    releaseDate = datetime(value[0],value[1],value[2],value[3],value[4],value[5])
    counterstart = releaseDate- timedelta(days=1)
    counter = 0
    print "now:",now
    print "counterstart:",counterstart
    print "release:",releaseDate
    if releaseDate >= now and now >= counterstart:
        counter = releaseDate-now
        print counter
        counter = counter.total_seconds()
        print counter
    return counter



@register.filter
def get_youtubevideo(value):
    print value
    import urlparse
    query = urlparse.urlparse(value)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = urlparse.parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    elif query.hostname in ('www.vimeo.com', 'vimeo.com'):
        return value
    # fail?
    return None

@register.filter
def highlight_mixtape(mixtape_id):

    sadd = AddonType.objects.get(name__iexact='Highlight Mixtape')
    highlights = AddonCharge.objects.prefetch_related().filter(
        addon=sadd,
        mixtape__approved=True,
        mixtape__releaseDatetime__lt=datetime.now(pytz.utc)
        )
    
    highlight = [g.object_id for g in highlights]
        #print coming
    highlight =Mixtape.objects.filter(approved=True, id__in=highlight).order_by('?')
    for mixtape in highlight:
        if mixtape.id == mixtape_id:
            return True
            break
    return False
        
    
