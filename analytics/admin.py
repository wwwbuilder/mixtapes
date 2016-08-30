from models import *
from django.contrib import admin


class AnalyticsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        analytics = Analytics.objects.all()
        if analytics:
            return False
        else:
            return True
        
admin.site.register(Analytics, AnalyticsAdmin)