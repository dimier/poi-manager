from poim.shared_settings import *


SITE_ID = 2

ROOT_URLCONF = 'poim_api.urls'

WSGI_APPLICATION = 'poim_api.wsgi.application'


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.locale.LocaleMiddleware',
]


INSTALLED_APPS += [
    'rest_framework',
]


DEFAULT_API_VERSION = (1, 0)

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'poim_api.utils.renderers.JSONRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_METADATA_CLASS': 'poim_api.utils.metadata.EmptyMetadata',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
}

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
]

CORS_EXPOSE_HEADERS = []

CORS_PREFLIGHT_MAX_AGE = 86400

CORS_ALLOW_CREDENTIALS = True


# Для документации
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.contrib.auth.context_processors.auth',
            ],
        },
    },
]
