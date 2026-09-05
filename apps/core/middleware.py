import logging
import re
import time
from uuid import uuid4

from .context import set_request_id

logger = logging.getLogger('apps.core.request')

REQUEST_ID_HEADER = 'X-Request-Id'

_SAFE_REQUEST_ID = re.compile(r'^[A-Za-z0-9._-]{1,64}$')


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = self._resolve_request_id(request)
        request.request_id = request_id
        set_request_id(request_id)
        started = time.monotonic()

        try:
            response = self.get_response(request)
        except Exception:
            logger.exception(
                'Unhandled exception while processing the request', extra=self._fields(request, 500, started)
            )
            raise

        response[REQUEST_ID_HEADER] = request_id
        logger.info(
            'Request processed',
            extra=self._fields(request, response.status_code, started),
        )
        return response

    @staticmethod
    def _resolve_request_id(request) -> str:
        incoming = request.headers.get(REQUEST_ID_HEADER)
        if incoming and _SAFE_REQUEST_ID.match(incoming):
            return incoming
        return uuid4().hex

    def _fields(self, request, status_code: int, started: float) -> dict:
        return {
            'method': request.method,
            'path': request.path,
            'status_code': status_code,
            'duration_ms': round((time.monotonic() - started) * 1000, 2),
            'user_id': self._resolve_user_id(request),
        }

    @staticmethod
    def _resolve_user_id(request):
        try:
            user = getattr(request, 'user', None)
            if user is not None and user.is_authenticated:
                return user.pk
        except Exception:
            return None
        return None
