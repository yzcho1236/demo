import math
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect


class PermRequired(PermissionRequiredMixin):
    def handle_no_permission(self):
        if self.raise_exception or self.request.user.is_authenticated:
            return HttpResponseRedirect("/index/?msg=用户没有访问的权限")


class ItemRequired(PermissionRequiredMixin):
    def handle_no_permission(self):
        if self.raise_exception or self.request.user.is_authenticated:
            return HttpResponseRedirect("/item/?msg=用户没有访问的权限")


class UserRequired(PermissionRequiredMixin):
    def handle_no_permission(self):
        if self.raise_exception or self.request.user.is_authenticated:
            return HttpResponseRedirect("/user/?msg=用户没有访问的权限")


class RoleRequired(PermissionRequiredMixin):
    def handle_no_permission(self):
        if self.raise_exception or self.request.user.is_authenticated:
            return HttpResponseRedirect("/role/?msg=用户没有访问的权限")


class PermissionRequired(PermissionRequiredMixin):
    def handle_no_permission(self):
        if self.raise_exception or self.request.user.is_authenticated:
            return HttpResponseRedirect("/perm/?msg=用户没有访问的权限")


class UserRoleRequired(PermissionRequiredMixin):
    def handle_no_permission(self):
        if self.raise_exception or self.request.user.is_authenticated:
            return HttpResponseRedirect("/user_role/?msg=用户没有访问的权限")


class RolePermRequired(PermissionRequiredMixin):
    def handle_no_permission(self):
        if self.raise_exception or self.request.user.is_authenticated:
            return HttpResponseRedirect("/role_permission/?msg=用户没有访问的权限")


class Pagination(object):
    def __init__(self, queryset, pagesize, page=1):
        self.page = page
        self.pagesize = pagesize
        self.queryset = queryset
        self.count = float(self.queryset.count())
        self.total_pages = int(math.ceil(self.count / self.pagesize))

    def get_objs(self):
        if self.page:
            self.page = int(self.page)
        if self.page > self.total_pages:
            self.page = self.total_pages
        if self.page < 1:
            self.page = 1
        cnt = (self.page - 1) * self.pagesize
        objs = self.queryset[cnt: cnt + self.pagesize]
        return objs


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



