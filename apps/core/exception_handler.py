import logging
import math

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404
from rest_framework import exceptions as drf_exceptions
from rest_framework.response import Response
from rest_framework.views import set_rollback

from . import errors
from .envelope import build_error_body

logger = logging.getLogger(__name__)

_DRF_TO_APP_ERROR = (
    (drf_exceptions.ParseError, errors.MalformedRequest),
    ((drf_exceptions.NotAuthenticated, drf_exceptions.AuthenticationFailed), errors.AuthenticationRequired),
    ((drf_exceptions.PermissionDenied, DjangoPermissionDenied), errors.PermissionDenied),
    ((drf_exceptions.NotFound, Http404), errors.NotFound),
    (drf_exceptions.MethodNotAllowed, errors.MethodNotAllowed),
    (drf_exceptions.Throttled, errors.RateLimitExceeded),
)


def api_exception_handler(exc, context):
    """EXCEPTION_HANDLER для DRF"""

    if isinstance(exc, errors.AppError):
        return _respond(exc, _headers_for(exc))

    if isinstance(exc, drf_exceptions.ValidationError):
        return _respond(
            errors.ValidationError(details=_flatten(exc.detail)),
            _headers_for(exc),
        )

    for exception_types, error_class in _DRF_TO_APP_ERROR:
        if isinstance(exc, exception_types):
            return _respond(error_class(), _headers_for(exc))

    if isinstance(exc, drf_exceptions.APIException):
        return _respond(
            errors.AppError(_plain_message(exc.detail), code='REQUEST_ERROR', http_status=exc.status_code),
            _headers_for(exc),
        )

    logger.exception(
        'Необработанное исключение в API',
        extra={'view': _view_name(context)},
    )
    return _respond(errors.InternalError(), {})


def _respond(error: errors.AppError, headers: dict) -> Response:
    set_rollback()
    return Response(
        build_error_body(error.code, error.message, error.details),
        status=error.http_status,
        headers=headers or None,
    )


def _headers_for(exc) -> dict:
    headers = {}

    auth_header = getattr(exc, 'auth_header', None)
    if auth_header:
        headers['WWW-Authenticate'] = auth_header

    wait = getattr(exc, 'wait', None)
    if wait is not None:
        headers['Retry-After'] = str(math.ceil(wait))

    return headers


def _flatten(detail, path: str = '') -> list[dict]:
    if isinstance(detail, dict):
        result = []
        for key, value in detail.items():
            result.extend(_flatten(value, f'{path}.{key}' if path else str(key)))
        return result

    if isinstance(detail, list):
        result = []
        for index, value in enumerate(detail):
            if isinstance(value, (dict, list)):
                result.extend(_flatten(value, f'{path}.{index}' if path else str(index)))
            else:
                result.extend(_flatten(value, path))
        return result

    return [{'field': path or None, 'message': str(detail)}]


def _plain_message(detail) -> str:
    if isinstance(detail, dict):
        return str(next(iter(detail.values()), ''))
    if isinstance(detail, list):
        return str(detail[0]) if detail else ''
    return str(detail)


def _view_name(context) -> str | None:
    view = (context or {}).get('view')
    if view is None:
        return None
    view_class = type(view)
    return f'{view_class.__module__}.{view_class.__name__}'
