from django.db import models
from _base.models import *
from django.utils.translation import ugettext as _

class Neighborhood(BaseClass):
    country = models.ForeignKey('locality.Country', related_name='neighborhoods')

    class Meta:
        verbose_name = _('Neighborhood')
        verbose_name_plural = _('Neighborhoods')