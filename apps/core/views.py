import logging
from uuid import uuid4

from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from stk_project import celery_app

from . import errors
from .envelope import build_error_body

logger = logging.getLogger(__name__)

PROBE_TIMEOUT_SECONDS = 2
PROBE_KEY_TTL_SECONDS = 60

class HealthView(APIView):
    authentication_classes = []  # noqa: RUF012
    permission_classes = [AllowAny]  # noqa: RUF012

    def get(self, request):
        return Response({'status': 'ok'})


def _check_database_connection() -> bool:
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
    except Exception:
        logger.exception('Failed to connect to database')
        return False
    return True


def _check_cache() -> bool:
    key = 'health_check:probe'
    value = uuid4().hex
    try:
        cache.set(key, value, timeout=PROBE_KEY_TTL_SECONDS)
        return cache.get(key) == value
    except Exception:
        logger.exception('Failed to connect to cache')
        return False


def _check_broker() -> bool:
    try:
        with celery_app.connection() as conn:
            conn.ensure_connection(
                max_retries=0,
                timeout=PROBE_TIMEOUT_SECONDS
            )
    except Exception:
        logger.exception('Failed to connect to broker')
        return False
    return True


class ReadyView(APIView):
    authentication_classes = [] # noqa: RUF012
    permission_classes = [AllowAny] # noqa: RUF012

    def get(self, request):
        checks = {
            'database': _check_database_connection(),
            'cache': _check_cache(),
            'broker': _check_broker(),
        }

        if not checks['database']:
            overall, http_status = 'error', status.HTTP_503_SERVICE_UNAVAILABLE
        elif all(checks.values()):
            overall, http_status = 'ok', status.HTTP_200_OK
        else:
            overall, http_status = 'degraded', status.HTTP_200_OK

        return Response(
            {'status': overall, 'checks': {name: 'ok' if ok else 'error' for name, ok in checks.items()}
             }, status=http_status,)


def _json_error(error: errors.AppError) -> JsonResponse:
    return JsonResponse(
        build_error_body(error.code, error.message, error.details),
        status=error.http_status,
        json_dumps_params={'ensure_ascii': False},
    )


def bad_request(request, exception):
    return _json_error(errors.MalformedRequest())


def permission_denied(request, exception):
    return _json_error(errors.PermissionDenied())


def not_found(request, exception):
    return _json_error(errors.NotFound())


def server_error(request):
    return _json_error(errors.InternalError())
