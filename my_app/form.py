from django import forms


class ItemBomForm(forms.Form):
    parent = forms.CharField(required=False)
    item = forms.CharField()
    nr = forms.CharField()
    effective_start = forms.DateField(required=False)
    effective_end = forms.DateField(required=False)
    qty = forms.IntegerField()
    files = forms.IntegerField(required=False)
