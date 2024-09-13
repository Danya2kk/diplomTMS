from celery.schedules import crontab
from datetime import timedelta
from pathlib import Path
import os.path




BASE_DIR = Path(__file__).resolve().parent.parent


STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

SECRET_KEY = "django-insecure-sw(omc%atk^)6&-ny+21_@nuemx(co6_ogjgjywrka9y+!)5+="

DEBUG = True

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "main",
    "corsheaders",
    "channels",
    "rest_framework",
    "rest_framework.authtoken",
    "djoser",
    "django_filters",
    "api",
    "drf_spectacular",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    # Наше middleware
    "main.middleware.UserActivityMiddleware",
]

ROOT_URLCONF = "socnet.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "socnet.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
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

USE_I18N = True

USE_TZ = True

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
    ),

    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
}


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


CORS_ALLOW_ALL_ORIGINS = True

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

AUTH_USER_MODEL = "main.User"


DJOSER = {
    "TOKEN_MODEL": "rest_framework.authtoken.models.Token",
    "LOGIN_FIELD": "email",
    "USER_CREATE_PASSWORD_RETYPE": True,
    "SERIALIZERS": {
        "user_create": "djoser.serializers.UserCreateSerializer",
        "user": "djoser.serializers.UserSerializer",
        "current_user": "djoser.serializers.UserSerializer",
    },
}

LOGOUT_REDIRECT_URL = "/"

LOGIN_REDIRECT_URL = "/"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"


CELERY_BEAT_SCHEDULE = {
    "archive-chat-daily": {
        "task": "socnet.tasks.archive_chat",
        "schedule": crontab(hour=0, minute=0),  # каждый день в полночь
    },
    "archive-mail-weekly": {
        "task": "socnet.tasks.archive_mail",
        "schedule": crontab(0, 0, day_of_week="sunday"),  # каждое воскресенье в полночь
        # 'schedule': crontab(minute='*/1'),  # Каждую минуту
    },
    "clean-mail-every-six-months": {
        "task": "socnet.tasks.clean_mail",
        "schedule": crontab(
            0, 0, day_of_month="1", month_of_year="*/6"
        ),  # 1-го числа каждые 6 месяцев
    },
    "update-online-status-every-5-minutes": {
        "task": "your_app_name.tasks.update_online_status",
        "schedule": crontab(minute="*/5"),  # Выполнять каждые 5 минут
    },
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "DEBUG",  # Уровень логирования для всех сообщений в консоли
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",  # Общий уровень логирования для Django
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "WARNING",  # Скрыть SQL-запросы (используется WARNING вместо DEBUG)
            "propagate": False,
        },
    },
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}



SPECTACULAR_SETTINGS = {

    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": True,

    },
    # available SwaggerUI versions: https://github.com/swagger-api/swagger-ui/releases
    "SWAGGER_UI_DIST": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest", # default
    "SWAGGER_UI_FAVICON_HREF": STATIC_URL + "your_company_favicon.png", # default is swagger favicon

}