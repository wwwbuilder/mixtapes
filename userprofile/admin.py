from django.contrib import admin
from .models import *
from _base.admin import BaseModelAdmin

class UserProfileAdmin(BaseModelAdmin):
    model = UserProfile
    list_display = ['username', 'premium',]
    search_fields = ['username',]
admin.site.register(UserProfile, UserProfileAdmin)