from django.contrib import admin

# Register your models here.
from my_app.models import BomModel


class BomAdmin(admin.ModelAdmin):
    change_form_template = 'bom.html'
    model = BomModel
    fields = ('nr', "item", "parent", "qty")
    list_display = ('nr', "item", "parent", "qty")
    # 弹窗
    raw_id_fields = ("item", "parent")

    # 只读
    readonly_fields = ("nr",)
    search_fields = ["item__nr"]


admin.site.register(BomModel, BomAdmin)


# class Comment_admin(admin.ModelAdmin):
#     model = Comment
#
#
# admin.site.register(Comment, Comment_admin)
