from django import forms


class BomForm(forms.Form):
    item = forms.CharField()
    child = forms.CharField()
    effective_start = forms.DateField(required=False)
    effective_end = forms.DateField(required=False)
    qty = forms.IntegerField()
