"""Peran panel.

* Superadmin (is_superuser): semua menu + kelola pengguna.
* Pengurus (is_staff): semua menu panel.
* Operator Display (is_staff + grup "Operator Display"): hanya menu Layar Masjid (display).
"""
OPERATOR_DISPLAY = 'Operator Display'

ROLE_PENGURUS = 'pengurus'
ROLE_OPERATOR = 'operator_display'
ROLE_CHOICES = [
    (ROLE_PENGURUS, 'Pengurus (semua menu panel)'),
    (ROLE_OPERATOR, 'Operator Display (hanya layar/monitor masjid)'),
]


def is_display_operator(user):
    if not getattr(user, 'is_authenticated', False) or user.is_superuser:
        return False
    cached = getattr(user, '_is_display_operator', None)
    if cached is None:
        cached = user.groups.filter(name=OPERATOR_DISPLAY).exists()
        user._is_display_operator = cached
    return cached


def role_of(user):
    if user.is_superuser:
        return 'superadmin'
    return ROLE_OPERATOR if is_display_operator(user) else ROLE_PENGURUS
