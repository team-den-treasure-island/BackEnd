from django.contrib import admin
from .models import Player, Room

# Register your models here.

# needed to see these fields on admin site
class TreasureHuntAdmin(admin.ModelAdmin):
    readonly_fields=('created_at', 'last_modified')

admin.site.register(Room, TreasureHuntAdmin)
admin.site.register(Player, TreasureHuntAdmin)
