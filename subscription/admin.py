from django.contrib import admin
from _base.admin import BaseModelAdmin
from .models import *

class PlanAdmin(BaseModelAdmin):
    model = Plan
    exclude = ('parent',)
    list_display = ('name', 'amount', 'currency', 'interval', 'category',)
    list_editable = ('amount', 'currency', 'interval', 'category',)

admin.site.register(Plan, PlanAdmin)

class PlanCategoryAdmin(BaseModelAdmin):
    model = PlanCategory

admin.site.register(PlanCategory, PlanCategoryAdmin)

class PlanFeatureAdmin(BaseModelAdmin):
    model = PlanFeature

admin.site.register(PlanFeature, PlanFeatureAdmin)