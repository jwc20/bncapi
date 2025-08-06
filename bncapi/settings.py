from pathlib import Path

from django.utils import timezone

BASE_DIR = Path(__file__).resolve().parent.parent

# TODO
SECRET_KEY = "django-insecure-*j8%_vh0y%g*iy0nm(rxp30%3r*#eb9@qgp82l(=6#&gn&v*si"
DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third party apps
    "corsheaders",
    "ninja_extra",
    # custom apps
    "knoxtokens",
    "users",
]

MIDDLEWARE = [
    # django default
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # cors middleware must be placed before CommonMiddleware
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
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


# TODO: change to Postgres
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


LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom User
AUTH_USER_MODEL = "users.User"


# Knox settings
AUTO_REFRESH = False
TOKEN_TTL = timezone.timedelta(days=90)
MIN_REFRESH_INTERVAL_SECOND = (60 * 60 * 24,)
HTTP_HEADER_ENCODING = "iso-8859-1"
AUTH_HEADER_PREFIX = "TOKEN"
AUTH_TOKEN_CHARACTER_LENGTH = 64
TOKEN_KEY_LENGTH = 15
DIGEST_LENGTH = 128
sha = "hashlib.sha512"
