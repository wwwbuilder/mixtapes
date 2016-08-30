from django.contrib import admin
from .models import *
from _base.admin import BaseModelAdmin

class ImageAdmin(BaseModelAdmin):
    model = Image
    list_display = ('name', 'filename', 'order', 'deleted',)
admin.site.register(Image, ImageAdmin)

