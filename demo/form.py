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
    parent = forms.CharField(required=False)


class UserForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(max_length=32)


class RegisterForm(forms.Form):
    username = forms.CharField()
    password1 = forms.CharField(max_length=32)
    password2 = forms.CharField(max_length=32)


class UserPwdForm(forms.Form):
    username = forms.CharField()
    password1 = forms.CharField(max_length=32)
    password2 = forms.CharField(max_length=32)


class UserEditForm(forms.Form):
    id = forms.IntegerField()
    username = forms.CharField()
    is_superuser = forms.CharField()


class RoleForm(forms.Form):
    id = forms.IntegerField()
    name = forms.CharField()


class RoleAddForm(forms.Form):
    name = forms.CharField()

