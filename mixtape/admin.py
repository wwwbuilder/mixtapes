from django.contrib import admin
from .models import *
from _base.admin import BaseModelAdmin

class MixtapeAdmin(BaseModelAdmin):
    model = Mixtape

    list_display = ('name', 'primaryGenre', 'approved', 'deleted','tracksurl')
    #list_filter = ('tracksurl', )
    exclude = ('order',)
    
    
admin.site.register(Mixtape, MixtapeAdmin)

class TrackAdmin(BaseModelAdmin):
    model = Track
    list_filter = ('mixtape', )
    list_display = ('id', 'filename', 'soundcloud_uri', 'deleted',)
  
    
    
admin.site.register(Track, TrackAdmin)




class GenreAdmin(BaseModelAdmin):
    model = Genre
admin.site.register(Genre, GenreAdmin)


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

class SpotLightAdmin(admin.ModelAdmin):
    model = MixtapeSpotLight
    #exclude = ('created',)
    list_display = ['title','image','artist']
admin.site.register(MixtapeSpotLight, SpotLightAdmin)


from django import forms
class GoogleAdsModelForm( forms.ModelForm ):
    content = forms.CharField( widget=forms.Textarea )
    class Meta:
        model = GoogleAdsBlock

class GoogleAdsBlock_Admin( admin.ModelAdmin ):
    form = GoogleAdsModelForm
    
    def has_add_permission(self, request):
            googleblock = GoogleAdsBlock.objects.all()
            if googleblock:
                return False
            else:
                return True    
    
admin.site.register(GoogleAdsBlock,GoogleAdsBlock_Admin)

admin.site.register(SoundCloudInfo)
