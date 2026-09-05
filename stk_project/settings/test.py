from urllib.parse import urlsplit, urlunsplit

from .base import *

DEBUG = False

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

_redis = urlsplit(REDIS_URL)
CACHES = {
    'default': {
        **CACHES['default'],
        'LOCATION': urlunsplit(_redis._replace(path='/1')),
    }
}

LOG_LEVEL = 'CRITICAL'
LOGGING['root']['level'] = LOG_LEVEL
for _logger_config in LOGGING['loggers'].values():
    _logger_config['level'] = LOG_LEVEL
