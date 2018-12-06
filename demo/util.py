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
