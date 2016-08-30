from django.db import models

# Create your models here.

class Analytics(models.Model):
    tracking_code = models.CharField(max_length=50, blank=True, null=True)
    
    def __unicode__(self):
        return '%s' % (self.tracking_code)    
