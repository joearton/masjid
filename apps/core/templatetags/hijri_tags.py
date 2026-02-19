"""
Hijri date template filters.

Usage in templates:
    {% load hijri_tags %}

    {{ date_value|hijri }}          →  "2 Ramadan 1447 H"
    {{ date_value|hijri_short }}    →  "2 Ram 1447"
    {{ date_value|hijri_full }}     →  "Kamis, 2 Ramadan 1447 H"
    {{ date_value|hijri_day }}      →  "2"
    {{ date_value|hijri_month }}    →  "Ramadan"
    {{ date_value|hijri_year }}     →  "1447"

Works with datetime.date, datetime.datetime, or Django DateTimeField values.
"""
from django import template
from hijridate import Gregorian
import datetime

register = template.Library()

# Indonesian names for Hijri months
HIJRI_MONTHS_ID = {
    1: 'Muharram',
    2: 'Safar',
    3: "Rabi'ul Awal",
    4: "Rabi'ul Akhir",
    5: 'Jumadil Awal',
    6: 'Jumadil Akhir',
    7: 'Rajab',
    8: "Sya'ban",
    9: 'Ramadan',
    10: 'Syawal',
    11: "Dzulqa'dah",
    12: 'Dzulhijjah',
}

# Indonesian day names
HARI_ID = {
    'Monday': 'Senin',
    'Tuesday': 'Selasa',
    'Wednesday': 'Rabu',
    'Thursday': 'Kamis',
    'Friday': 'Jumat',
    'Saturday': 'Sabtu',
    'Sunday': 'Ahad',
}


def _to_date(value):
    """Convert value to datetime.date."""
    if value is None:
        return None
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    return None


def _to_hijri(value):
    """Convert a date/datetime to Hijri object."""
    d = _to_date(value)
    if d is None:
        return None
    try:
        return Gregorian(d.year, d.month, d.day).to_hijri()
    except (ValueError, OverflowError):
        return None


@register.filter(name='hijri')
def hijri_date(value):
    """
    Convert Gregorian date to Hijri: "2 Ramadan 1447 H"
    """
    h = _to_hijri(value)
    if h is None:
        return ''
    month_name = HIJRI_MONTHS_ID.get(h.month, h.month_name())
    return f"{h.day} {month_name} {h.year} H"


@register.filter(name='hijri_short')
def hijri_short(value):
    """
    Short Hijri format: "2 Ram 1447"
    """
    h = _to_hijri(value)
    if h is None:
        return ''
    month_name = HIJRI_MONTHS_ID.get(h.month, h.month_name())
    return f"{h.day} {month_name[:3]} {h.year}"


@register.filter(name='hijri_full')
def hijri_full(value):
    """
    Full Hijri format with day name: "Kamis, 2 Ramadan 1447 H"
    """
    h = _to_hijri(value)
    if h is None:
        return ''
    d = _to_date(value)
    day_en = h.day_name()
    day_id = HARI_ID.get(day_en, day_en)
    month_name = HIJRI_MONTHS_ID.get(h.month, h.month_name())
    return f"{day_id}, {h.day} {month_name} {h.year} H"


@register.filter(name='hijri_day')
def hijri_day(value):
    """Return just the Hijri day number."""
    h = _to_hijri(value)
    return h.day if h else ''


@register.filter(name='hijri_month')
def hijri_month(value):
    """Return the Hijri month name in Indonesian."""
    h = _to_hijri(value)
    if h is None:
        return ''
    return HIJRI_MONTHS_ID.get(h.month, h.month_name())


@register.filter(name='hijri_year')
def hijri_year(value):
    """Return just the Hijri year."""
    h = _to_hijri(value)
    return h.year if h else ''


@register.simple_tag
def hijri_today():
    """Return today's Hijri date string: '2 Ramadan 1447 H'"""
    today = datetime.date.today()
    h = Gregorian(today.year, today.month, today.day).to_hijri()
    month_name = HIJRI_MONTHS_ID.get(h.month, h.month_name())
    return f"{h.day} {month_name} {h.year} H"


@register.simple_tag
def hijri_today_full():
    """Return today's full Hijri date: 'Kamis, 2 Ramadan 1447 H'"""
    today = datetime.date.today()
    h = Gregorian(today.year, today.month, today.day).to_hijri()
    day_id = HARI_ID.get(h.day_name(), h.day_name())
    month_name = HIJRI_MONTHS_ID.get(h.month, h.month_name())
    return f"{day_id}, {h.day} {month_name} {h.year} H"
