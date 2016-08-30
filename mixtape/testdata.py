from .models import *
from userprofile.models import *
from django.utils.text import slugify

def populate():

    genre_titles = [u'Hip Hop', u'R&B', u'Rock', u'Pop', u'Techno']


    print '\n================================'
    print 'GENRES'
    print '================================'

    for t in genre_titles:
        obj, created = Genre.objects.get_or_create(name=t)
        if created:
            print '%s -- CREATED!' % obj.name
        else:
            print '%s -- ALREADY EXISTS!' % obj.name

    print '\n================================'
    print 'ARTISTS'
    print '================================'

    genres = Genre.objects.all()
    people_types = [u'Artist', u'Producer', u'DJ']

    for g in genres:
        for p in people_types:
            for i in range(1, 11):
                obj, created = UserProfile.objects.get_or_create(
                    username='%s %s %s' % (g.name, p, i),
                    official=True,
                    homepage='http://www.%s-%s-%s.com' % (g.name, p, i),
                    facebook='http://facebook.com/%s%s%s' % (g.name, p, i),
                    twitter='http://twitter.com/%s%s%s' % (g.name, p, i),
                    google='http://googleplus.com/%s%s%s' % (g.name, p, i),
                    youtube='http://youtube.com/%s%s%s' % (g.name, p, i),
                    video='http://youtube.com/%s%s%s-video' % (g.name, p, i),
                    pinterest='http://pinterest.com/%s%s%s' % (g.name, p, i),
                    soundcloud='http://soundcloud.com/%s%s%s' % (g.name, p, i),
                    aboutme='Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'
                    )
                obj.genres.add(g)
                print '%s -- CREATED!' % obj.username