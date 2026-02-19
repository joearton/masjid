"""Sholat forms."""
from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Row, Column
from .models import JadwalJumat, SholatSettings



class SholatSettingsForm(forms.ModelForm):
    class Meta:
        model = SholatSettings
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                _('Konfigurasi Lokasi (AdhanPy)'),
                Row(
                    Column('latitude', css_class='col-md-4'),
                    Column('longitude', css_class='col-md-4'),
                    Column('timezone', css_class='col-md-4'),
                ),
            ),
            Fieldset(
                _('Koreksi Waktu (Menit)'),
                Row(
                    Column('koreksi_subuh', css_class='col-md-2'),
                    Column('koreksi_dzuhur', css_class='col-md-2'),
                    Column('koreksi_ashar', css_class='col-md-2'),
                    Column('koreksi_maghrib', css_class='col-md-2'),
                    Column('koreksi_isya', css_class='col-md-2'),
                ),
                css_class='mt-3 mb-3'
            ),
            Submit('submit', _('Simpan Pengaturan'), css_class='btn btn-primary')
        )


class JadwalJumatForm(forms.ModelForm):
    class Meta:
        model = JadwalJumat
        fields = '__all__'
        widgets = {
            'tanggal': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', _('Simpan'), css_class='btn btn-primary'))
