"""Pembantu bersama API MyUMKO Masjid: galat seragam, batas laju, paginasi, kelas dasar.

Semua pengaturan DRF dipasang per kelas view, bukan lewat REST_FRAMEWORK global,
sehingga panel dan situs web masjid tidak berubah perilakunya. Gaya mengikuti
mobile_api BAA.
"""
import ipaddress

from django.conf import settings
from django.core.cache import caches
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404
from django.utils import timezone
from rest_framework import exceptions, generics, permissions, status
from rest_framework.negotiation import BaseContentNegotiation
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.views import APIView
from rest_framework.views import exception_handler as drf_handler

DEFAULT_THROTTLE_RATE = '300/min'


# ------------------------------------------------------------------ galat
class ApiError(exceptions.APIException):
    """Galat dengan ``code`` mesin dan isian tambahan opsional."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'invalid'

    def __init__(self, detail, code=None, status_code=None, errors=None, **extra):
        super().__init__(detail, code)
        if status_code:
            self.status_code = status_code
        self.code = code or self.default_code
        self.errors = errors
        self.extra = extra


def not_found(detail='Data tidak ditemukan.'):
    return ApiError(detail, code='not_found', status_code=status.HTTP_404_NOT_FOUND)


def invalid_param(name, message):
    """400 ``invalid`` dengan galat per parameter kueri."""
    return ApiError('Parameter tidak valid.', code='invalid', errors={name: [message]})


def _indonesian_detail(exc):
    """Pesan bawaan DRF berbahasa Inggris  → Indonesia."""
    if isinstance(exc, exceptions.Throttled):
        wait = exc.wait
        if wait:
            return f'Terlalu banyak permintaan. Coba lagi dalam {int(wait + 0.999)} detik.'
        return 'Terlalu banyak permintaan. Coba lagi nanti.'
    if isinstance(exc, exceptions.MethodNotAllowed):
        return 'Metode tidak diizinkan untuk alamat ini.'
    if isinstance(exc, exceptions.NotAcceptable):
        return 'Format respons yang diminta tidak didukung.'
    if isinstance(exc, exceptions.NotFound):
        return 'Data tidak ditemukan.'
    if isinstance(exc, exceptions.PermissionDenied):
        return 'Anda tidak berhak mengakses data ini.'
    if isinstance(exc, exceptions.ParseError):
        return 'Isi permintaan tidak dapat dibaca.'
    return None


def exception_handler(exc, context):
    """Bentuk galat seragam: ``{"detail", "code", "errors"?}``."""
    if isinstance(exc, Http404):
        exc = not_found()
    elif isinstance(exc, DjangoPermissionDenied):
        exc = exceptions.PermissionDenied()
    response = drf_handler(exc, context)
    if response is None:
        return None
    data = response.data
    body = {'detail': '', 'code': getattr(exc, 'code', None) or getattr(exc, 'default_code', 'error')}
    if isinstance(exc, ApiError):
        body['detail'] = str(exc.detail)
        if exc.errors:
            body['errors'] = exc.errors
        body.update(exc.extra)
    elif isinstance(data, dict) and 'detail' in data:
        codes = exc.get_codes() if hasattr(exc, 'get_codes') else None
        body['code'] = codes.get('detail', body['code']) if isinstance(codes, dict) else (codes or body['code'])
        detail = str(data['detail'])
        # Pesan khusus (mis. paginasi) dipertahankan; pesan bawaan DRF diterjemahkan.
        if detail == str(getattr(exc, 'default_detail', '')) or isinstance(exc, (exceptions.Throttled,
                                                                                 exceptions.MethodNotAllowed)):
            detail = _indonesian_detail(exc) or detail
        body['detail'] = detail
    else:
        body['detail'] = 'Periksa kembali isian Anda.'
        body['code'] = 'invalid'
        body['errors'] = data if isinstance(data, dict) else {'non_field_errors': data}
    response.data = body
    response['Cache-Control'] = 'no-store'
    return response


# ------------------------------------------------------------------ IP klien
# Rentang IP resmi Cloudflare (https://www.cloudflare.com/ips/), sama dengan
# Transforma. Situs masjid dilayani OpenLiteSpeed → gunicorn (127.0.0.1), sehingga
# REMOTE_ADDR selalu alamat proksi; tanpa penelusuran X-Forwarded-For batas laju
# per IP akan berlaku untuk semua pengguna sekaligus.
CLOUDFLARE_NETWORKS = [ipaddress.ip_network(n) for n in (
    '173.245.48.0/20', '103.21.244.0/22', '103.22.200.0/22', '103.31.4.0/22',
    '141.101.64.0/18', '108.162.192.0/18', '190.93.240.0/20', '188.114.96.0/20',
    '197.234.240.0/22', '198.41.128.0/17', '162.158.0.0/15', '104.16.0.0/13',
    '104.24.0.0/14', '172.64.0.0/13', '131.0.72.0/22',
    '2400:cb00::/32', '2606:4700::/32', '2803:f800::/32', '2405:b500::/32',
    '2405:8100::/32', '2a06:98c0::/29', '2c0f:f248::/32',
)]


def _is_trusted_proxy(ip):
    return ip.is_loopback or ip.is_private or any(ip in net for net in CLOUDFLARE_NETWORKS)


def client_ip(request):
    """IP klien asli: rantai X-Forwarded-For ditelusuri dari kanan, melewati hop
    tepercaya (Cloudflare, lokal, privat)."""
    chain = [p.strip() for p in request.META.get('HTTP_X_FORWARDED_FOR', '').split(',') if p.strip()]
    remote = request.META.get('REMOTE_ADDR', '')
    for candidate in reversed(chain + [remote] if remote else chain):
        try:
            ip = ipaddress.ip_address(candidate)
        except ValueError:
            return candidate
        if not _is_trusted_proxy(ip):
            return candidate
    return chain[0] if chain else remote


# ------------------------------------------------------------------ batas laju
class AnonThrottle(SimpleRateThrottle):
    """Batas laju per IP. Penghitung di cache 'default' (diambil saat dipakai agar
    cache pengujian ikut berlaku). Cache bawaan: memori per proses (1 worker gunicorn)."""
    scope = 'mobile_anon'

    @property
    def cache(self):
        return caches['default']

    def get_rate(self):
        rates = getattr(settings, 'MOBILE_API_THROTTLE_RATES', {}) or {}
        return rates.get(self.scope) or DEFAULT_THROTTLE_RATE

    def get_cache_key(self, request, view):
        return self.cache_format % {'scope': self.scope, 'ident': client_ip(request._request) or self.get_ident(request)}


# ------------------------------------------------------------------ paginasi
class Pagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50
    invalid_page_message = 'Halaman {page_number} tidak ditemukan.'


# ------------------------------------------------------------------ negosiasi
class JSONOnlyNegotiation(BaseContentNegotiation):
    """Selalu JSON, apa pun header Accept dari klien (tidak pernah 406).
    Ekspor .ics mengembalikan HttpResponse langsung sehingga tidak terpengaruh."""

    def select_parser(self, request, parsers):
        return parsers[0] if parsers else None

    def select_renderer(self, request, renderers, format_suffix=None):
        return (renderers[0], renderers[0].media_type)


def today():
    """Hari ini di zona Asia/Jakarta (TIME_ZONE situs)."""
    return timezone.localdate()


def cache_seconds():
    return int(getattr(settings, 'MOBILE_API_CACHE_SECONDS', 300))


# ------------------------------------------------------------------ kelas dasar
class MobileAPIMixin:
    """Publik tanpa autentikasi, JSON saja, galat seragam, batas laju per IP, cache publik."""
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    renderer_classes = [JSONRenderer]
    parser_classes = []
    content_negotiation_class = JSONOnlyNegotiation
    throttle_classes = [AnonThrottle]
    pagination_class = Pagination

    def get_exception_handler(self):
        return exception_handler

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        if (request.method in ('GET', 'HEAD') and 200 <= response.status_code < 300
                and not response.has_header('Cache-Control')):
            response['Cache-Control'] = f'public, max-age={cache_seconds()}'
        return response


class MobileAPIView(MobileAPIMixin, APIView):
    pass


class MobileListView(MobileAPIMixin, generics.ListAPIView):
    pass


class NotFoundView(MobileAPIView):
    """Penampung path tak dikenal di bawah /api/mobile/v1/ → 404 JSON."""
    schema = None

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        raise not_found('Alamat API tidak ditemukan.')
