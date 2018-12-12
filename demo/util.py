import math
from functools import wraps

import six
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.decorators import available_attrs


def perm_required(perm, login_url=None, raise_exception=False):
    def check_perms(user):
        if isinstance(perm, six.string_types):
            perms = (perm,)
        else:
            perms = perm
        # First check if the user has the permission (even anon users)
        if user.has_perms(perms):
            return True
        # In case the 403 handler should be called raise the exception
        if raise_exception:
            return PermissionDenied
        # As the last resort, show the login form
        return False

    return passes_test(check_perms, login_url=login_url)


def passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            return redirect("/item/?msg=用户没有权限")

        return _wrapped_view

    return decorator


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

    def get_objs(self):
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
