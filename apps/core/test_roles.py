from unittest import mock

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from apps.core.roles import OPERATOR_DISPLAY, is_display_operator
from apps.display.models import DisplaySettings


@mock.patch('apps.display.views.get_prayer_times')
class OperatorDisplayTests(TestCase):
    def setUp(self):
        self.display = DisplaySettings.objects.create(nama='TV', is_default=True)
        self.op = User.objects.create_user('operator', password='x', is_staff=True)
        self.op.groups.add(Group.objects.get(name=OPERATOR_DISPLAY))  # dibuat oleh migrasi
        self.pengurus = User.objects.create_user('pengurus', password='x', is_staff=True)
        self.admin = User.objects.create_superuser('admin', password='x')

    def test_group_has_display_permissions(self, _):
        codes = set(Group.objects.get(name=OPERATOR_DISPLAY).permissions.values_list('codename', flat=True))
        self.assertIn('change_displaysettings', codes)
        self.assertIn('add_displayslide', codes)

    def test_operator_only_reaches_display(self, _):
        self.client.force_login(self.op)
        self.assertTrue(is_display_operator(self.op))
        self.assertEqual(self.client.get(reverse('display:panel_settings_list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('display:panel_settings_edit', args=[self.display.pk])).status_code, 200)
        r = self.client.post(reverse('display:ajax_display_save', args=[self.display.pk]), {'tema': 'gold'})
        self.assertEqual(r.status_code, 200)
        # dasbor: dialihkan tanpa pesan; menu lain: dialihkan dengan pesan
        r = self.client.get(reverse('panel:dashboard'))
        self.assertRedirects(r, reverse('display:panel_settings_list'), fetch_redirect_response=False)
        for name in ('berita:panel_list', 'keuangan:panel_list', 'panel:site_setting', 'sholat:panel_settings', 'panel:user_list'):
            r = self.client.get(reverse(name))
            self.assertEqual(r.status_code, 302, name)
            self.assertEqual(r['Location'], reverse('display:panel_settings_list'), name)
        page = self.client.get(reverse('display:panel_settings_list'))
        self.assertNotContains(page, reverse('berita:panel_list'))
        self.assertContains(page, 'Operator Display')

    def test_pengurus_full_menu_but_no_user_admin(self, _):
        self.client.force_login(self.pengurus)
        self.assertEqual(self.client.get(reverse('berita:panel_list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('panel:user_list')).status_code, 302)

    def test_superadmin_creates_and_changes_operator(self, _):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse('panel:user_list')).status_code, 200)
        r = self.client.post(reverse('panel:user_create'), {
            'username': 'petugas_tv', 'first_name': 'Petugas TV', 'email': '', 'is_active': 'on',
            'role': 'operator_display', 'password1': 'Layar-Masjid-2026', 'password2': 'Layar-Masjid-2026'})
        self.assertEqual(r.status_code, 302, getattr(r, 'context', None) and r.context['form'].errors)
        u = User.objects.get(username='petugas_tv')
        self.assertTrue(u.is_staff and u.check_password('Layar-Masjid-2026'))
        self.assertTrue(is_display_operator(u))
        self.client.post(reverse('panel:user_edit', args=[u.pk]), {
            'username': 'petugas_tv', 'first_name': 'Petugas TV', 'email': '', 'is_active': 'on', 'role': 'pengurus',
            'password1': '', 'password2': ''})
        u = User.objects.get(pk=u.pk)
        self.assertFalse(is_display_operator(u))
        self.assertTrue(u.check_password('Layar-Masjid-2026'))
        self.assertEqual(self.client.get(reverse('panel:user_edit', args=[self.admin.pk])).status_code, 404)
