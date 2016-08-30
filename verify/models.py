from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from _base.models import *
from twilio.rest import TwilioRestClient
from django.utils.translation import ugettext as _


class TwilioVerification(GenericFKBaseClass):
    '''
    The use of a generic foreign key allows us to verify more than just the user.
    Perhaps we will later verify mixtape uploads after approval, etc.
    '''

    user = models.ForeignKey(User, related_name='twilio_verifications')
    body = models.TextField()
    to = models.IntegerField()
    from__user = models.IntegerField()
    pin = models.CharField(max_length=6, blank=True)
    verified = models.BooleanField(default=False)
    sid = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = _('Twilio Verification')
        verbose_name_plural = _('Twilio Verifications')

    def send_text(self):
        client = TwilioRestClient(settings.TWILIO_ACCOUNT, settings.TWILIO_TOKEN)
        message = client.messages.create(
            to=self.to,
            from_=self.from_,
            body=self.body
            )
        self.sid = message.sid
        self.save()