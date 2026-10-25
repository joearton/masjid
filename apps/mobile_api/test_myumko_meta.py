"""Pengaturan bagian masjid di MyUMKO lewat GET meta/: features, lokasi jadwal bawaan, pengumuman."""
import datetime as dt
from unittest import mock

from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from apps.core.forms import SiteSettingForm
from apps.core.models import SiteSetting
from apps.profil.models import ProfilMasjid
from apps.sholat.models import SholatSettings

API = '/api/mobile/v1/'


class MyumkoMetaTests(TestCase):
    def setUp(self):
        cache.clear()
        offline = mock.patch('urllib.request.urlopen', side_effect=OSError('offline'))
        offline.start()
        self.addCleanup(offline.stop)
        SholatSettings.objects.create()
        ProfilMasjid.objects.create(nama='Masjid Uji', sejarah='s', visi='v', misi='m', alamat='Kotabumi')

    def meta(self):
        cache.clear()
        resp = self.client.get(API + 'meta/')
        self.assertEqual(resp.status_code, 200)
        return resp.json()

    def test_defaults(self):
        data = self.meta()
        self.assertEqual(data['features'], {'jadwal': True, 'jumat': True, 'kegiatan': True, 'berita': True,
                                            'keuangan': True, 'donasi': False, 'profil': True})
        self.assertEqual(data['jadwal_sholat']['default_location'], {'jenis': 'masjid', 'kota_id': None})
        self.assertIsNone(data['pengumuman'])

    def test_settings_reflected(self):
        site = SiteSetting.load()
        site.myumko_kegiatan = False
        site.myumko_lokasi_bawaan = SiteSetting.LOKASI_KOTA
        site.myumko_kota_bawaan = '1816'
        site.myumko_pengumuman = 'Sholat Idul Adha di lapangan'
        site.myumko_pengumuman_url = 'https://masjid.umko.ac.id/'
        site.myumko_pengumuman_nada = 'warning'
        site.save()
        data = self.meta()
        self.assertFalse(data['features']['kegiatan'])
        self.assertEqual(data['jadwal_sholat']['default_location'], {'jenis': 'kota', 'kota_id': '1816'})
        self.assertEqual(data['pengumuman'], {'text': 'Sholat Idul Adha di lapangan', 'url': 'https://masjid.umko.ac.id/',
                                              'tone': 'warning', 'until': None})

    def test_expired_announcement_hidden(self):
        site = SiteSetting.load()
        site.myumko_pengumuman = 'Lama'
        site.myumko_pengumuman_sampai = timezone.now() - dt.timedelta(minutes=1)
        site.save()
        self.assertIsNone(self.meta()['pengumuman'])
        site.myumko_pengumuman_sampai = timezone.now() + dt.timedelta(days=1)
        site.save()
        self.assertEqual(self.meta()['pengumuman']['text'], 'Lama')

    def test_form_requires_valid_city(self):
        site = SiteSetting.load()
        base = {f: getattr(site, f) for f in SiteSettingForm._meta.fields or [] if hasattr(site, f)}
        form = SiteSettingForm(instance=site, data={**base, 'myumko_lokasi_bawaan': 'kota', 'myumko_kota_bawaan': 'abc'})
        self.assertFalse(form.is_valid())
        self.assertIn('myumko_kota_bawaan', form.errors)
        with mock.patch('apps.sholat.kemenag.find_city', return_value=None):
            form = SiteSettingForm(instance=site, data={'myumko_lokasi_bawaan': 'kota', 'myumko_kota_bawaan': '9999'})
            form.is_valid()
            self.assertIn('myumko_kota_bawaan', form.errors)
        with mock.patch('apps.sholat.kemenag.find_city', return_value=object()):
            form = SiteSettingForm(instance=site, data={'myumko_lokasi_bawaan': 'kota', 'myumko_kota_bawaan': '1816'})
            form.is_valid()
            self.assertNotIn('myumko_kota_bawaan', form.errors)


class PanelMyumkoTabTests(TestCase):
    """Formulir panel memakai semua kolom model: setiap kolom MyUMKO wajib punya input di template,
    kalau tidak, menyimpan pengaturan lain akan me-reset sakelarnya ke False dan mengosongkan teksnya."""

    def test_every_myumko_field_has_input(self):
        from django.contrib.auth import get_user_model
        admin = get_user_model().objects.create_superuser('admin', 'a@example.com', 'x')
        self.client.force_login(admin)
        resp = self.client.get('/panel/pengaturan/')
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        self.assertIn('id="pane-myumko"', html)
        for field in SiteSetting._meta.get_fields():
            if field.name.startswith('myumko_'):
                self.assertIn(f'name="{field.name}"', html, field.name)
