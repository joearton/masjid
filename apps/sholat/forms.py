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
                _('Sumber Jadwal'),
                'sumber',
                Row(
                    Column('kota_kemenag_id', css_class='col-md-4'),
                    Column('kota_kemenag_nama', css_class='col-md-8'),
                ),
            ),
            Fieldset(
                _('Lokasi Masjid (untuk hisab)'),
                Row(
                    Column('latitude', css_class='col-md-3'),
                    Column('longitude', css_class='col-md-3'),
                    Column('elevasi', css_class='col-md-2'),
                    Column('ihtiyat', css_class='col-md-2'),
                    Column('timezone', css_class='col-md-2'),
                ),
                css_class='mt-3'
            ),
            Fieldset(
                _('Koreksi Tambahan (menit, biasanya 0)'),
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

    def clean_timezone(self):
        from zoneinfo import ZoneInfo
        value = self.cleaned_data['timezone']
        try:
            ZoneInfo(value)
        except Exception:
            raise forms.ValidationError(_('Zona waktu tidak dikenal. Contoh: Asia/Jakarta'))
        return value

    def clean(self):
        data = super().clean()
        lat, lon = data.get('latitude'), data.get('longitude')
        if lat is not None and not -90 <= lat <= 90:
            self.add_error('latitude', _('Latitude harus antara -90 dan 90.'))
        if lon is not None and not -180 <= lon <= 180:
            self.add_error('longitude', _('Longitude harus antara -180 dan 180.'))
        return data


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
