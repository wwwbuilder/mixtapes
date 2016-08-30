from django.db import models
from datetime import datetime
import pytz
from _base.mixins import NotDeletedManager, NotDeletedQuerySet

class MixtapeQuerySet(NotDeletedQuerySet):
    def approved(self):
        return self.filter(approved=True)

    def released(self):
        return self.filter(releaseDatetime__lte=pytz.utc.localize(datetime.now()))

    def public(self):
        return self.filter(
            releaseDatetime__lte=pytz.utc.localize(datetime.now()), 
            approved=True,
            deleted=False
            )

class MixtapeManager(NotDeletedManager):
    def get_queryset(self):
        return MixtapeQuerySet(self.model)

    def approved(self, *args, **kwargs):
        return self.get_query_set().approved(*args, **kwargs)

    def released(self, *args, **kwargs):
        return self.get_query_set().released(*args, **kwargs)

    def public(self, *args, **kwargs):
        return self.get_query_set().public(*args, **kwargs)