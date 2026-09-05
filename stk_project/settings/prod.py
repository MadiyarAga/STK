from .base import *
from .env import env_list

DEBUG = False
ALLOWED_HOSTS = env_list('DJANGO_ALLOWED_HOSTS', 'разрешённые имена хостов')
