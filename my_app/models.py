from datetime import datetime

from django.db import models

from input.models import Item


class BomModel(models.Model):
    id = models.AutoField(primary_key=True)
    nr = models.CharField(max_length=300, unique=True, verbose_name="代码")
    item = models.ForeignKey(
        Item, verbose_name="物料", on_delete=models.CASCADE, related_name="bom_item")
    parent = models.ForeignKey(
        Item, verbose_name="父类",
        null=True, blank=True, on_delete=models.CASCADE, related_name="bom_parent"
    )
    qty = models.IntegerField(verbose_name="数量")
    effective_start = models.DateField(verbose_name="生效开始", null=True, blank=True,
                                       default=datetime(datetime.now().year, datetime.now().month, datetime.now().day))
    effective_end = models.DateField(verbose_name="生效结束", null=True, blank=True, default=datetime(2030, 12, 31))

    def __str__(self):
        return self.nr

    class Meta:
        app_label = "my_app"
        unique_together = (('item', 'parent'),)
