from django.contrib import admin
from .models import *
from _base.admin import BaseModelAdmin

class AddonTypeAdmin(BaseModelAdmin):
    model = AddonType
    exclude = ['order', 'parent',]
    list_display = ['name', 'price', 'duration', 'description', 'category', ]
    list_editable = ['price', 'duration', 'description', 'category', ]
admin.site.register(AddonType, AddonTypeAdmin)

class AddonCategoryAdmin(BaseModelAdmin):
    model = AddonCategory
    exclude = ['order',]
    list_display = ['name',]
admin.site.register(AddonCategory, AddonCategoryAdmin)