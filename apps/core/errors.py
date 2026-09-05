"""Доменные исключения.

Модуль намеренно не импортирует ни Django, ни DRF: одно и то же
правило обязано срабатывать при вызове из API, из задачи Celery и из скрипта
наполнения. Как только AppError потянет за собой rest_framework, доменный слой
окажется привязан к HTTP."""


class AppError(Exception):
    """Базовое доменное исключение"""

    code: str = 'INTERNAL_ERROR'
    message: str = 'Внутренняя ошибка сервера.'
    http_status: int = 500

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        details: list[dict] | None = None,
        http_status: int | None = None,
    ) -> None:
        cls = type(self)
        self.code = code or cls.code
        self.message = message or cls.message
        self.http_status = cls.http_status if http_status is None else http_status
        self.details = details
        super().__init__(self.message)

    def __str__(self):
        return f'{self.code}: {self.message}'


class ValidationError(AppError):
    code: str = 'VALIDATION_ERROR'
    message: str = 'Переданные данные не прошли проверку.'
    http_status: int = 422


class MalformedRequest(AppError):
    code: str = 'MALFORMED_REQUEST'
    message: str = 'Некорректный запрос.'
    http_status: int = 400


class AuthenticationRequired(AppError):
    code = 'AUTHENTICATION_REQUIRED'
    message = 'Требуется аутентификация.'
    http_status = 401


class PermissionDenied(AppError):
    code: str = 'PERMISSION_DENIED'
    message: str = 'Недостаточно прав.'
    http_status: int = 403


class NotFound(AppError):
    code: str = 'NOT_FOUND'
    message: str = 'Ресурс не найден.'
    http_status: int = 404


class MethodNotAllowed(AppError):
    code: str = 'METHOD_NOT_ALLOWED'
    message: str = 'Метод запрещен.'
    http_status: int = 405


class RateLimitExceeded(AppError):
    code: str = 'RATE_LIMIT_EXCEEDED'
    message: str = 'Превышен лимит запросов.'
    http_status: int = 429


class InternalError(AppError):
    code: str = 'INTERNAL_ERROR'
    message: str = 'Внутренняя ошибка сервера.'
    http_status: int = 500


# --- Конфликты состояния (409) ---


class ConflictError(AppError):
    code: str = 'CONFLICT'
    message: str = 'Конфликт данных.'
    http_status: int = 409


class InsufficientStock(ConflictError):
    code = 'INSUFFICIENT_STOCK'
    message = 'Недостаточно товара на складе.'


class IdempotentKeyConflict(ConflictError):
    code = 'IDEMPOTENT_KEY_CONFLICT'
    message = 'Ключ идемпотентности уже использован.'


class InvalidStatusTransition(ConflictError):
    code = 'INVALID_STATUS_TRANSITION'
    message = 'Недопустимое состояние.'


# --- Ошибки данных (422) ---


class RecipeCycleDetected(ValidationError):
    code = 'RECIPE_CYCLE_DETECTED'
    message = 'Обнаружена циклическая зависимость техкарты.'
