from django.contrib import admin

# Register your models here.
from input.models import Item
from my_app.models import Pictures


class ItemAdmin(admin.ModelAdmin):
    model = Item
    fields = ('nr', 'name', 'barcode')


admin.site.register(Item, ItemAdmin)


class PictureAdmin(admin.ModelAdmin):
    model = Pictures


admin.site.register(Pictures, PictureAdmin)
