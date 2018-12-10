from django import forms


class ItemForm(forms.Form):
    id = forms.IntegerField()
    nr = forms.CharField()
    name = forms.CharField()
    barcode = forms.CharField()


class ItemAddForm(forms.Form):
    nr = forms.CharField()
    name = forms.CharField()
    barcode = forms.CharField()


class UserForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()


class RegisterForm(forms.Form):
    username = forms.CharField()
    password1 = forms.CharField()
    password2 = forms.CharField()


class UserEditForm(forms.Form):
    id = forms.IntegerField()
    username = forms.CharField()
    password = forms.CharField()
    is_superuser = forms.CharField()


class RoleForm(forms.Form):
    id = forms.IntegerField()
    name = forms.CharField()


class RoleAddForm(forms.Form):
    name = forms.CharField()


class PermissionAddForm(forms.Form):
    codename = forms.CharField()
    name = forms.CharField()
