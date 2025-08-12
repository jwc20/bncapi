from pathlib import Path

import dj_database_url
from django.utils import timezone
from corsheaders.defaults import default_headers
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "secret")
DEBUG = os.getenv("DEBUG", "True").lower()

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "bncapi.onrender.com", "0.0.0.0"]

INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third party apps
    "corsheaders",
    "ninja",
    "silk",
    "channels",
    # custom apps
    "knoxtokens",
    "users",
    "games",
]

MIDDLEWARE = [
    # django default
    "django.middleware.security.SecurityMiddleware",
    # for serving static files
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # cors middleware must be placed before CommonMiddleware
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "silk.middleware.SilkyMiddleware",
]

ROOT_URLCONF = "bncapi.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "bncapi.wsgi.application"


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


LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"


if DEBUG:
    STATIC_ROOT = os.path.join(BASE_DIR, "static/")

if not DEBUG:
    # Tell Django to copy static assets into a path called `staticfiles` (this is specific to Render)
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

    # Enable the WhiteNoise storage backend, which compresses static files to reduce disk use
    # and renames the files with unique names for each version to support long-term caching
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom User
AUTH_USER_MODEL = "users.User"


# Knox settings
AUTO_REFRESH = False
TOKEN_TTL = timezone.timedelta(days=90)
MIN_REFRESH_INTERVAL_SECOND = (60 * 60 * 24,)
HTTP_HEADER_ENCODING = "iso-8859-1"
# AUTH_HEADER_PREFIX = "TOKEN"
AUTH_HEADER_PREFIX = "Bearer"
AUTH_TOKEN_CHARACTER_LENGTH = 64
TOKEN_KEY_LENGTH = 8
DIGEST_LENGTH = 128

# allow all origins
CORS_ALLOW_ALL_ORIGINS = True
# allow all methods
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
# allow all headers
CORS_ALLOW_HEADERS = list(default_headers) + [
    "app-version",
    "os-type",
    "token",
    "api-key",
]
# allow all credentials
CORS_ALLOW_CREDENTIALS = True

# for django-channels
ASGI_APPLICATION = "bncapi.asgi.application"

REDIS_CHANNEL_LAYER_URL = os.environ.get("REDIS_CHANNEL_LAYER_URL")
if REDIS_CHANNEL_LAYER_URL:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [REDIS_CHANNEL_LAYER_URL],
            },
        },
    }

else:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [
                    (
                        os.getenv("REDIS_HOST", "0.0.0.0"),
                        int(os.getenv("REDIS_PORT", 6379)),
                    )
                ],
            },
        },
    }
# postgres
POSTGRES_DATABASE_URL = os.getenv("POSTGRES_DATABASE_URL")
if POSTGRES_DATABASE_URL:
    DATABASES = {"default": dj_database_url.parse(POSTGRES_DATABASE_URL)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "postgres"),
            "USER": os.getenv("POSTGRES_USER", "postgres"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
            "HOST": os.getenv("POSTGRES_HOST", "0.0.0.0"),
            "PORT": int(os.getenv("POSTGRES_PORT", 5432)),
        }
    }

# sqlite (commented out - use for local development if needed)
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

PUBLIC_API_URL = os.getenv("PUBLIC_API_URL", "http://127.0.0.1:8000/api")
