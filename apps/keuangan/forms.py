"""Keuangan forms."""
from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import TransaksiKeuangan, KategoriKeuangan


class TransaksiKeuanganForm(forms.ModelForm):
    class Meta:
        model = TransaksiKeuangan
        fields = '__all__'
        widgets = {
            'tanggal': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', _('Simpan'), css_class='btn btn-primary'))


class KategoriKeuanganForm(forms.ModelForm):
    class Meta:
        model = KategoriKeuangan
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', _('Simpan'), css_class='btn btn-primary'))
