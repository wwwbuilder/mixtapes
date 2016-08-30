from django.db import models
from _base.models import BaseClass, GenericFKBaseClass
from django.utils.translation import ugettext as _
import pytz

class AddonCategory(BaseClass):
    pass

    class Meta:
        verbose_name = _('Addon Category')
        verbose_name_plural = _('Addon Categories')

    def __unicode__(self):
        return '%s' % self.name
    


class AddonType(BaseClass):
    category = models.ForeignKey('addon.AddonCategory', blank=True, null=True, related_name='addontypes')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    duration = models.IntegerField(blank=True, null=True, help_text='Duration in days')

    class Meta(GenericFKBaseClass.Meta):
        verbose_name = _('Addon Type')
        verbose_name_plural = _('Addon Types')


class AddonCharge(GenericFKBaseClass):
    end_datetime = models.DateTimeField(blank=True, null=True)
    charge = models.ForeignKey('payments.Charge', related_name='addon_charges')
    addon = models.ForeignKey('addon.AddonType')

    # @classmethod
    # def create_charge(cls, userobj, addonobj, mixtapeobj):
    #     cu = userobj.customer
    #     ao = addonobj
    #     mt = mixtapeobj
    #     char = cu.charge(amount=Decimal(ao.price), description=addonobj.title)
    #     print '%s charge created for %s' % (ao.title, userobj.username)
    #     if ao.duration:
    #         edt = datetime.now(pytz.utc) + relativedelta(days=ao.duration)
    #     else:
    #         edt = None
    #     ac = AddonCharge(
    #         end_datetime = edt,
    #         charge = char,
    #         addon = ao,
    #         mixtape = mt
    #         )
    #     ac.save()

    #     tweet = MixtapeAddon.objects.get(title='Tweet Mixtape Release')
    #     #Create tweet if this is the tweet addon
    #     if ac.addon == tweet and ac.id:
    #         Tweet.maketweet(ac.mixtape)
    #     return ac

    # @property
    # def status(self):
    #     if self.end_date < datetime.now(pytz.utc):
    #         return 'expired'
    #     elif self.end_date > datetime.now(pytz.utc):
    #         return 'active'