import sys
from .base import *


# DEBUG = False

# DATABASES['default']['USER'] = ''

TESTING = bool(len(sys.argv) > 1 and sys.argv[1] == 'test')


# django делает прозрачное применение миграций при запуске тестов;
# аргумент --keep-db более надёжно сохраняет БД, чем переменная окружения.
INSTALLED_APPS += [
    # 'django_nose',
]


# Выполняет захват stdout и логов по тестам
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'


if TESTING:
    CACHES['default'] = {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }

    PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]

    EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
