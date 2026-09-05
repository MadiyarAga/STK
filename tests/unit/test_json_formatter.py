import json
import logging
import sys

from apps.core.logging import JsonFormatter


def _record(**overrides) -> logging.LogRecord:
    params = {
        'name': 'tests',
        'level': logging.INFO,
        'pathname': __file__,
        'lineno': 1,
        'msg': 'сообщение',
        'args': (),
        'exc_info': None,
    }
    params.update(overrides)
    return logging.LogRecord(**params)


def test_message_arguments_are_substituted():
    payload = json.loads(JsonFormatter().format(_record(msg='x=%s', args=(5,))))

    assert payload['message'] == 'x=5'


def test_traceback_is_not_lost():
    try:
        raise ValueError('тестовое падение')
    except ValueError:
        exc_info = sys.exc_info()

    payload = json.loads(JsonFormatter().format(_record(exc_info=exc_info)))

    assert 'ValueError: тестовое падение' in payload['exception']


def test_unserializable_value_does_not_break_logging():
    record = _record()
    record.user_id = object()

    assert 'user_id' in json.loads(JsonFormatter().format(record))


def test_field_outside_the_whitelist_is_dropped():
    record = _record()
    record.authorization = 'Bearer секретный-токен'

    assert 'authorization' not in json.loads(JsonFormatter().format(record))
