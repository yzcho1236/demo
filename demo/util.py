import math
from functools import wraps
from urllib.parse import urlunparse, urlparse

import six
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect

from input.models import Item


def perm_required(perm, raise_exception=False):
    def check_perms(user):
        if isinstance(perm, six.string_types):
            perms = (perm,)
        else:
            perms = perm
        if user.has_perms(perms):
            return True
        if raise_exception:
            return PermissionDenied
        return False

    return passes_test(check_perms)


def passes_test(test_func):
    def decorator(view_func):
        # 获取当前请求的对象
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            return HttpResponseRedirect("/index/?msg=用户没有访问的权限")

        return _wrapped_view

    return decorator


class Pagination(object):
    def __init__(self, queryset, pagesize, page=1):
        self.pagesize = pagesize
        self.queryset = queryset
        self.count = float(self.queryset.count())
        self.total_pages = int(math.ceil(self.count / self.pagesize))
        self.page = page
        if self.page:
            self.page = int(self.page)
        if self.page > self.total_pages:
            self.page = self.total_pages
        if self.page < 1:
            self.page = 1

        self.prev = 1 if self.page == 1 else self.page - 1
        self.next = self.page if self.page == self.total_pages else self.page + 1

    def get_objs(self):
        cnt = (self.page - 1) * self.pagesize
        objs = self.queryset[cnt: cnt + self.pagesize]
        return objs


class GetItemParent(object):
    @staticmethod
    def get_parent():
        items = Item.objects.all().order_by("id").values("id", "nr")
        item_all = {}
        for i in items:
            item_all[i["id"]] = i["nr"]
        return item_all


_filter_map_jqgrid_django = {
    'ne': ('%(field)s__iexact', True),
    'bn': ('%(field)s__istartswith', True),
    'en': ('%(field)s__iendswith', True),
    'nc': ('%(field)s__icontains', True),
    'ni': ('%(field)s__in', True),
    'in': ('%(field)s__in', False),
    'eq': ('%(field)s__iexact', False),
    'bw': ('%(field)s__istartswith', False),
    'gt': ('%(field)s__gt', False),
    'ge': ('%(field)s__gte', False),
    'lt': ('%(field)s__lt', False),
    'le': ('%(field)s__lte', False),
    'ew': ('%(field)s__iendswith', False),
    'cn': ('%(field)s__icontains', False)
}
select_op = {'eq': '等于', 'ne': '不等于', 'lt': '小于', 'le': '小于等于', 'gt': '大于等于', 'bw': '开始于', 'bn': '不开始于', 'in': '属于',
             'ni': '不属于', 'cn': '包含', 'nc': '不包含'}
