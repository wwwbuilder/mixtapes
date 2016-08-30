from mixtape import models, sc

def run():
    for mt in models.Mixtape.objects.filter(approved=True, soundcloud_permalink=''):
        sc.soundcloudSend(mt)
