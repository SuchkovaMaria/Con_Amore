import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

IN_DOCKER = os.path.exists("/.dockerenv")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "con_amore",
    "users",
    "django_celery_beat",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

if IN_DOCKER:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("NAME"),
            "USER": os.getenv("USER"),
            "PASSWORD": os.getenv("PASSWORD"),
            "HOST": "db",
            "PORT": os.getenv("PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("NAME"),
            "USER": os.getenv("USER"),
            "PASSWORD": os.getenv("PASSWORD"),
            "HOST": os.getenv("HOST"),
            "PORT": os.getenv("PORT"),
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "ru"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True  # → поддержка языков
USE_L10N = True  # → локальные форматы чисел/дат
USE_TZ = True  # Использовать часовые пояса (рекомендуется)


STATIC_URL = "static/"

STATICFILES_DIRS = [BASE_DIR / "static"]

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "media/"

MEDIA_ROOT = os.path.join(BASE_DIR / "media")

AUTH_USER_MODEL = "users.User"

LOGIN_REDIRECT_URL = "con_amore:home"
LOGOUT_REDIRECT_URL = "con_amore:home"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.yandex.ru"
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

SERVER_EMAIL = EMAIL_HOST_USER

CACHE_ENABLED = True
if CACHE_ENABLED:
    if IN_DOCKER:
        CACHES = {
            "default": {
                "BACKEND": "django.core.cache.backends.redis.RedisCache",
                "LOCATION": os.getenv(
                    "DOCKER_REDIS_URL",
                ),
            }
        }
    else:
        CACHES = {
            "default": {
                "BACKEND": "django.core.cache.backends.redis.RedisCache",
                "LOCATION": os.getenv(
                    "HOST_CACHE",
                ),
            }
        }

CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

if IN_DOCKER:
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
else:
    CELERY_BROKER_URL = os.getenv("DOCKER_CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.getenv("DOCKER_CELERY_RESULT_BACKEND")

CELERY_BEAT_SCHEDULE = {
    "user_deactivation": {
        "task": "con_amore.tasks.mail_about_reservation_execution",
        "schedule": timedelta(minutes=1),
    },
}

CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
