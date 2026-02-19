"""Kegiatan forms."""
from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import Kegiatan


class KegiatanForm(forms.ModelForm):
    class Meta:
        model = Kegiatan
        fields = '__all__'
        widgets = {
            'tanggal': forms.DateInput(attrs={'type': 'date'}),
            'waktu_mulai': forms.TimeInput(attrs={'type': 'time'}),
            'waktu_selesai': forms.TimeInput(attrs={'type': 'time'}),
            'deskripsi': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.add_input(Submit('submit', _('Simpan'), css_class='btn btn-primary'))
