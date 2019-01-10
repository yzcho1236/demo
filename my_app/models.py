from datetime import datetime
from django.utils import timezone

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from input.models import Item, User


class Comment(models.Model):
    id = models.AutoField('identifier', primary_key=True)
    # 指向ContentType的外键
    content_type = models.ForeignKey(
        ContentType, verbose_name='content type',
        related_name="content_type",
        on_delete=models.CASCADE)
    # 对象的主键
    object_pk = models.TextField('object id')
    # 评论的对象
    content_object = GenericForeignKey(ct_field="content_type", fk_field="object_pk")
    # 用upload_to来指定文件存放的前缀路径
    img = models.ImageField(upload_to="img", verbose_name="图片", null=True, blank=True)
    file = models.FileField(upload_to="file", verbose_name="文件", null=True, blank=True)
    user = models.ForeignKey(
        User, verbose_name='user', blank=True, null=True,
        editable=False, on_delete=models.CASCADE)
    upload_time = models.DateTimeField(verbose_name="上传时间", null=True, blank=True, default=timezone.now())


class UploadFileModel(models.Model):
    id = models.AutoField('identifier', primary_key=True)
    # 指向ContentType的外键
    content_type = models.ForeignKey(
        ContentType, verbose_name='content type',
        related_name="upload_file",
        on_delete=models.CASCADE)
    # 对象的主键
    object_pk = models.TextField('object id')
    # 评论的对象
    content_object = GenericForeignKey(ct_field="content_type", fk_field="object_pk")
    # 用upload_to来指定文件存放的前缀路径
    img = models.CharField(verbose_name="图片", null=True, blank=True, max_length=500)
    img_url = models.CharField(verbose_name="图片", null=True, blank=True, max_length=500)
    file = models.CharField(verbose_name="文件", null=True, blank=True, max_length=500)
    file_url = models.CharField(verbose_name="文件地址", null=True, blank=True, max_length=500)
    user = models.ForeignKey(
        User, verbose_name='user', blank=True, null=True,
        editable=False, on_delete=models.CASCADE)
    upload_time = models.DateTimeField(verbose_name="上传时间", null=True, blank=True, default=timezone.now())


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

    annex = GenericRelation(UploadFileModel, verbose_name='附件', related_name='bom_comment', object_id_field='object_pk')

    def __str__(self):
        return self.nr

    class Meta:
        app_label = "my_app"
        unique_together = (('item', 'parent'),)


class Pictures(models.Model):
    pic = models.ImageField(upload_to='img/')

    def __str__(self):
        return self.pic
