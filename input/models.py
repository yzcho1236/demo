from django.contrib.auth.models import AbstractUser, Permission
from django.db import models


class Perm(models.Model):
    """权限"""
    id = models.AutoField('id', primary_key=True)
    name = models.CharField(max_length=300, unique=True, verbose_name="名称")
    codename = models.CharField(max_length=300, unique=True, verbose_name="名称代码")

    class Meta:
        permissions = (('view_item', "can view item"),
                       ('view_user', "can view user"),
                       ('view_user_role', "can view user role"),
                       ('view_role', "can view role"),
                       ('view_role_permission', "can view role permission"),
                       )


class Role(models.Model):
    """角色"""
    id = models.AutoField('id', primary_key=True)
    name = models.CharField(max_length=300, unique=True, verbose_name="角色名称")

    def __str__(self):
        return self.name


class User(AbstractUser):
    """用户"""
    def has_perm(self, perm, obj=None):
        # 获取用户关联的所有角色对象
        if self.is_active and self.is_superuser:
            return True
        else:
            roles = UserRole.objects.filter(user=self.id).values_list('role_id')
            return RolePermission.objects.filter(role_id__in=roles, permission__codename=perm).exists()

            # role_perm = []
            # # 获取用户权限对象列表
            # for i in roles:
            #     # 查询角色关联的所有权限
            #     perms = RolePermission.objects.filter(role=i.role).values("permission__codename")
            #     perms_list = [i["permission__codename"] for i in list(perms)]
            #     if perm in perms_list:
            #         return True


class RolePermission(models.Model):
    """角色权限"""
    id = models.AutoField('id', primary_key=True)
    role = models.ForeignKey(
        Role, verbose_name="角色",
        null=True, blank=True, on_delete=models.CASCADE,
    )
    permission = models.ForeignKey(
        Perm, verbose_name="权限",
        null=True, blank=True, on_delete=models.CASCADE,
    )


class UserRole(models.Model):
    """用户角色"""
    id = models.AutoField('id', primary_key=True)
    role = models.ForeignKey(
        Role, verbose_name="角色",
        null=True, blank=True, on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User, verbose_name="用户",
        null=True, blank=True, on_delete=models.CASCADE,
    )


class Item(models.Model):
    """物料"""
    id = models.AutoField(primary_key=True)
    nr = models.CharField(max_length=300, unique=True, verbose_name="代码")
    name = models.CharField(max_length=300, verbose_name="名称")
    barcode = models.CharField(max_length=300, verbose_name="条码")
