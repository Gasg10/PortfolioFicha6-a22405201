from pathlib import Path
import os
import environ

env = environ.Env()
environ.Env.read_env(os.path.join(Path(__file__).resolve().parent.parent, ".env"))

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-#+5ih9afezvw*w=urf-b6=zothlzzk=9mvwgd^e-wizk^nt3-a'

DEBUG = True

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = [
    'https://reimagined-spork-g45qg79rrwxr3pwgr-8000.app.github.dev',
    'https://localhost:8000',
    'http://localhost:8000',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'portfolio',
    'escola',
    'markdownify.apps.MarkdownifyConfig',
    'accounts',
    'artigos',
    'cloudinary',
    'cloudinary_storage',
]

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/portfolio/'
LOGOUT_REDIRECT_URL = '/portfolio/'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

DATABASES = {
    "default": env.db("DATABASE_URL")
}

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': env('CLOUDINARY_API_KEY'),
    'API_SECRET': env('CLOUDINARY_API_SECRET'),
}

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-pt'

TIME_ZONE = 'Europe/Lisbon'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MARKDOWNIFY = {
    "default": {
        "WHITELIST_TAGS": [
            'a', 'abbr', 'acronym',
            'strong', 'b',
            'blockquote', 'em', 'i',
            'ul', 'li', 'ol',
            'p',
            'h1', 'h2', 'h3', 'h4',
        ]
    }
}
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')
