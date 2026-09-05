import json
import logging
from datetime import UTC, datetime

from .context import get_request_id

_EXTRA_FIELDS = (
    'request_id',
    'user_id',
    'method',
    'path',
    'status_code',
    'duration_ms',
    'view',
)


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            'timestamp': datetime.fromtimestamp(record.created, UTC).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }

        for field in _EXTRA_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value

        if record.exc_info:
            payload['exception'] = self.formatException(record.exc_info)
        elif record.exc_text:
            payload['exception'] = record.exc_text

        if record.stack_info:
            payload['stack'] = self.formatStack(record.stack_info)

        return json.dumps(payload, default=str, ensure_ascii=False)
