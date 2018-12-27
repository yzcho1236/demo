from django import forms


class BomForm(forms.Form):
    parent_id = forms.IntegerField()
    parent = forms.CharField()
    parent_nr = forms.CharField()
    item = forms.CharField()
    item_nr = forms.CharField()
    effective_start = forms.DateField(required=False)
    effective_end = forms.DateField(required=False)
    qty = forms.IntegerField()


class BomEditForm(forms.Form):
    id = forms.IntegerField()
    name = forms.CharField()
    effective_start = forms.DateField(required=False)
    effective_end = forms.DateField(required=False)
    qty = forms.IntegerField()
