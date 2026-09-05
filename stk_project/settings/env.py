import os

from django.core.exceptions import ImproperlyConfigured

_UNSET = object()


def _raw(name: str) -> str | object:
    """Единственная функция в модуле, которая читает os.environ.
    Возвращает непустую строку либо _UNSET, если переменная не задана
    или состоит только из пробелов."""

    value = os.environ.get(name, "").strip()

    return value if value else _UNSET


def _missing(name: str, purpose: str, default):
    """Обрабатывает отсутствие значения: либо падаем, либо отдаём default как есть."""

    if default is _UNSET:
        raise ImproperlyConfigured(
            f"Переменная окружения '{name}' не настроена. "
            f"Назначение: {purpose}."
        )

    return default


def env_str(name: str, purpose: str, default=_UNSET) -> str:
    """Читает строковое значение из os.environ. Пустая строка расценивается как отсутствие значения."""

    value = _raw(name)

    if value is _UNSET:
        return _missing(name, purpose, default)

    return value


def env_bool(name: str, purpose: str, default=_UNSET) -> bool:
    """Читает логическое значение из os.environ. Принимает 1/0, true/false, yes/no, on/off в любом регистре.
    Любое другое значение вызывает ImproperlyConfigured."""

    value = _raw(name)

    if value is _UNSET:
        return _missing(name, purpose, default)

    normalized = value.lower()

    if normalized in ("1", "true", "yes", "on"):
        return True

    if normalized in ("0", "false", "no", "off"):
        return False

    raise ImproperlyConfigured(
        f"Некорректное логическое значение для '{name}': '{value}'. "
        f"Допустимы: 1/0, true/false, yes/no, on/off. "
        f"Назначение: {purpose}."
    )


def env_int(name: str, purpose: str, default=_UNSET) -> int:
    """Читает целочисленное значение из os.environ. Любое нечисловое значение вызывает ImproperlyConfigured."""

    value = _raw(name)

    if value is _UNSET:
        return _missing(name, purpose, default)

    try:
        return int(value)
    except ValueError:
        raise ImproperlyConfigured(
            f"Значение переменной '{name}' должно быть целым числом, "
            f"получено: '{value}'. Назначение: {purpose}."
        ) from None


def env_list(name: str, purpose: str, default=_UNSET) -> list[str]:
    """Читает список строк из os.environ, разделённых запятой.
    Обрезает пробелы по краям элементов и удаляет пустые элементы.
    Значение, состоящее только из разделителей, отклоняется, а не превращается
    в пустой список.
    """

    value = _raw(name)

    if value is _UNSET:
        return _missing(name, purpose, default)

    items = [item.strip() for item in value.split(",") if item.strip()]

    if not items:
        raise ImproperlyConfigured(
            f"Переменная '{name}' задана, но не содержит ни одного элемента: '{value}'. "
            f"Ожидается список через запятую. Назначение: {purpose}."
        )

    return items
