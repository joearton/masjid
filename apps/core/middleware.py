"""Batasi percobaan masuk yang gagal per alamat IP (panel dan django-admin)."""
from django.core.cache import cache
from django.http import HttpResponse

LOGIN_PATHS = ('/panel/login/', '/en/panel/login/', '/django-admin/login/')
MAX_FAILURES = 8
WINDOW = 15 * 60


def client_ip(request):
    ip = request.META.get('HTTP_CF_CONNECTING_IP')
    if not ip:
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
        ip = forwarded.split(',')[0].strip() if forwarded else request.META.get('REMOTE_ADDR', '')
    return ip


class LoginThrottleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method != 'POST' or request.path not in LOGIN_PATHS:
            return self.get_response(request)
        key = f'login-gagal:{client_ip(request)}'
        if cache.get(key, 0) >= MAX_FAILURES:
            return HttpResponse('Terlalu banyak percobaan masuk. Coba lagi 15 menit lagi.',
                                status=429, content_type='text/plain; charset=utf-8')
        response = self.get_response(request)
        if response.status_code == 200:  # formulir ditampilkan ulang = gagal masuk
            try:
                cache.incr(key)
            except ValueError:
                cache.set(key, 1, WINDOW)
        elif response.status_code in (301, 302):
            cache.delete(key)
        return response
