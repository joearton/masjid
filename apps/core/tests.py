import datetime as dt
from unittest import mock

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase

from apps.core.templatetags.hijri_tags import _to_date
from apps.display.models import DisplaySettings, DisplaySlide

OFFLINE = mock.patch('urllib.request.urlopen', side_effect=OSError('offline'))


class PanelSecurityTests(TestCase):
    def setUp(self):
        cache.clear()
        self.staff = User.objects.create_user('pengurus', password='Rahasia-123', is_staff=True)
        self.user = User.objects.create_user('jamaah', password='Rahasia-123')

    def test_non_staff_blocked_from_panel(self):
        self.client.force_login(self.user)
        for url in ('/panel/', '/panel/pengaturan/', '/keuangan/panel/report/'):
            resp = self.client.get(url)
            self.assertNotEqual(resp.status_code, 200, url)
            self.assertLess(resp.status_code, 500, url)

    def test_logout_via_post(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.post('/panel/logout/').status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_respects_safe_next_only(self):
        resp = self.client.post('/panel/login/?next=/sholat/panel/settings/',
                                {'username': 'pengurus', 'password': 'Rahasia-123'})
        self.assertEqual(resp['Location'], '/sholat/panel/settings/')
        self.client.logout()
        resp = self.client.post('/panel/login/?next=https://evil.example/',
                                {'username': 'pengurus', 'password': 'Rahasia-123'})
        self.assertEqual(resp['Location'], '/panel/')

    def test_login_throttle(self):
        for _ in range(8):
            self.client.post('/panel/login/', {'username': 'pengurus', 'password': 'salah'})
        resp = self.client.post('/panel/login/', {'username': 'pengurus', 'password': 'Rahasia-123'})
        self.assertEqual(resp.status_code, 429)

    def test_display_api_requires_staff(self):
        d = DisplaySettings.objects.create(nama='TV', tema='default')
        anon = self.client.post(f'/display/{d.pk}/update/', {'tema': 'dark'})
        self.assertEqual(anon.status_code, 403)
        d.refresh_from_db()
        self.assertEqual(d.tema, 'default')
        self.client.force_login(self.staff)
        self.assertEqual(self.client.post(f'/display/{d.pk}/update/', {'tema': 'dark'}).status_code, 200)

    def test_editing_slide_keeps_display(self):
        d = DisplaySettings.objects.create(nama='TV')
        slide = DisplaySlide.objects.create(display=d, judul='Himbauan', tipe='teks')
        self.client.force_login(self.staff)
        resp = self.client.post(f'/display/panel/settings/slides/{slide.pk}/edit/', {
            'judul': 'Himbauan baru', 'tipe': 'teks', 'durasi': 10, 'urutan': 1, 'aktif': 'on', 'konten_teks': 'x'})
        self.assertEqual(resp.status_code, 302)
        slide.refresh_from_db()
        self.assertEqual(slide.display_id, d.pk)

    def test_public_donor_signup_waits_for_confirmation(self):
        from apps.donatur.models import Donatur
        with OFFLINE:
            self.client.post('/donatur/register/', {'nama': 'Hamba Allah', 'telepon': '0812', 'tipe': 'tetap',
                                                  'komitmen_rutin': 50000, 'tipe_rutin': 'bulanan'})
            self.client.post('/donatur/register/', {'nama': 'Bot', 'telepon': '1', 'tipe': 'tetap',
                                                  'komitmen_rutin': 0, 'website': 'spam'})
        self.assertEqual(list(Donatur.objects.values_list('nama', 'status')), [('Hamba Allah', 'baru')])


class HijriTests(TestCase):
    def test_aware_datetime_uses_local_date(self):
        value = dt.datetime(2026, 10, 9, 20, 0, tzinfo=dt.timezone.utc)
        self.assertEqual(_to_date(value), dt.date(2026, 10, 10))
