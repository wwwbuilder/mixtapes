from django.db import models
from _base.models import *
from django.utils.translation import ugettext as _
from django.conf import settings

class PlanCategory(BaseClass):
    pass

    class Meta:
        verbose_name = _('Plan Category')
        verbose_name_plural = _('Plan Categories')

    def __unicode__(self):
        return '%s' % self.name


class Plan(BaseClass):
    category = models.ForeignKey('subscription.PlanCategory', blank=True, null=True)
    amount = models.IntegerField(help_text='$6.99 displayed as 699')
    currency = models.CharField(max_length=50, default='usd')
    livemode = models.BooleanField(default=True)
    features = models.ManyToManyField('subscription.PlanFeature', blank=True, null=True)
    
    INTERVAL_CHOICES = (
        ('week', _('week')),
        ('month', _('month')),
        ('year', _('year')),
        )
    interval = models.CharField(max_length=50, choices=INTERVAL_CHOICES, blank=True, null=True)
    interval_count = models.IntegerField(default=1)
    metadata = models.CharField(max_length=200, blank=True, null=True)
    trial_period_days = models.IntegerField(blank=True, null=True)
    statement_description = models.CharField(max_length=50, blank=True, null=True)
    stripe_id = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = _('Plan')
        verbose_name_plural = _('Plans')

    def create_stripe_plans(self):
        pass


class PlanFeature(BaseClass):
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _('Plan Feature')
        verbose_name_plural = _('Plan Features')

    def __unicode__(self):
        return '%s' % self.name
    