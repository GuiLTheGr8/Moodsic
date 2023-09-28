from django.contrib import admin

from.models import Playlist, Moodsic

class MoodsicAdmin(admin.ModelAdmin):
    exclude = ('typedText',)

# Register your models here.
admin.site.register(Playlist)
admin.site.register(Moodsic, MoodsicAdmin)