import logging
from datetime import datetime

from django.contrib.auth.models import AbstractUser, Permission
from django.db import models, DEFAULT_DB_ALIAS, transaction, connections


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
    display_key = None
    id = models.AutoField(primary_key=True)
    nr = models.CharField(max_length=300, unique=True, verbose_name="代码")
    name = models.CharField(max_length=300, verbose_name="名称")
    barcode = models.CharField(max_length=300, verbose_name="条码")
    effective_start = models.DateField(verbose_name="生效开始", null=True, blank=True,
                                       default=datetime(datetime.now().year, datetime.now().month, datetime.now().day))
    effective_end = models.DateField(verbose_name="生效结束", null=True, blank=True, default=datetime(2030, 12, 31))

    # 左节点
    lft = models.PositiveIntegerField(null=True, blank=True, verbose_name="左节点")
    # 右节点
    rght = models.PositiveIntegerField(null=True, blank=True, verbose_name="右节点")
    # 层级
    lvl = models.PositiveIntegerField(null=True, blank=True, verbose_name="层级")
    parent = models.ForeignKey('self', null=True, blank=True, related_name='xchildren', on_delete=models.CASCADE,
                               verbose_name="父类")

    def __str__(self):
        return self.nr

    # def set_ancestor(self):
    #     if self.parent is None:
    #         self.ancestor = None
    #     else:
    #
    #         self.ancestor = ""

    def save(self, *args, **kwargs):
        self.lft = None
        self.rght = None
        self.lvl = None
        # self.set_ancestor()
        super(Item, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            # Update an arbitrary other object to trigger recalculation of the hierarchy
            obj = self.__class__.objects.using(self._state.db).exclude(pk=self.pk)[0]
            obj.lft = None
            obj.rght = None
            obj.lvl = None
            obj.save(
                update_fields=['lft', 'rght', 'lvl'],
                using=self._state.db
            )
        except:
            pass
        super(Item, self).delete(*args, **kwargs)

    @classmethod
    def rebuild_item(cls, database=DEFAULT_DB_ALIAS):

        # 判断是否有左节点为空的
        if len(cls.objects.using(database).filter(lft__isnull=True)[:1]) == 0:
            return

        # 节点 A为子类物料名称，2 为父类ID {"A":2}
        nodes = {}

        # 所有节点 {"2": {'A'}}
        children = {}

        # 所有根节点的左节点有节点和层级 [(left, right, level, me),(left, right, level, me)]
        updates = []

        def tagChildren(me, left, level):
            right = left + 1
            for i in children.get(me, []):
                right = tagChildren(i, right, level + 1)

            updates.append((left, right, level, me))

            del nodes[me]

            return right + 1

        display_key = cls.display_key if cls.display_key else 'nr'

        # 获取所有的物料名称对应的父类ID    如：i = {"name":'A', "parent":2}
        for i in cls.objects.using(database).values(display_key, 'parent__nr'):
            # 如果自己的父类是自身
            if i[display_key] == i['parent__nr']:
                logging.error("Data error: '%s' points to itself as owner" % i[display_key])
                nodes[i[display_key]] = None
            else:
                # node:{"A":2} 物料名称对应的父类ID
                nodes[i[display_key]] = i['parent__nr']
                # 如果有父类ID且父类不在子类字典中
                if i['parent__nr']:
                    if not i['parent__nr'] in children:
                        children[i['parent__nr']] = set()
                    children[i['parent__nr']].add(i[display_key])  # children = {"2": {'A'}}
        keys = sorted(nodes.items())

        # 遍历所有节点，如果是根节点设置它的right值，删除根节点
        cnt = 1
        for i, j in keys:
            if j is None:
                cnt = tagChildren(i, cnt, 0)

        # TODO 不知道这是用来干什么？
        if nodes:
            bad_list = []
            bad = nodes.copy()
            for i in bad.keys():
                for j, k in bad.items():
                    if k == i:
                        bad_list.append(i)
            logging.error("Data error: Hierarchy loops among %s" % sorted(bad.keys()))

            for i in bad_list:
                nodes[i] = None

            keys = sorted(nodes.items())
            for i, j in keys:
                if j is None:
                    cnt = tagChildren(i, cnt, 0)

        # 批量更新
        with transaction.atomic(using=database):
            connections[database].cursor().executemany(
                'update %s set lft=%%s, rght=%%s, lvl=%%s where name = %%s' % connections[database].ops.quote_name(
                    cls._meta.db_table),
                updates)


"""WITH recursive T (id, name, parent_id, path, depth)  as (
    select id, name, parent_id, ARRAY[id] AS path, 1 as depth
    from input_item
    where parent_id is null
    union all
    select  D.id, D.name, D.parent_id, T.path || D.id, T.depth + 1 as depth
    from input_item D
    join T on D.parent_id = T.id
    )
    select id, name, parent_id, path, depth from T
order by path;
"""