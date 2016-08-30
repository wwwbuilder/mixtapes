from django.contrib import admin
from guardian.admin import GuardedModelAdmin

class BaseModelAdmin(GuardedModelAdmin):
    actions_on_bottom = True
    save_as = True
    save_on_top = True
    search_fields = ['name']
    list_display = ['name']
    list_select_related = True
    readonly_fields = ['created_by', 'updated_by', 'created', 'updated', 'slug',]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        if not change:
            obj.created_by = request.user
        obj.save()