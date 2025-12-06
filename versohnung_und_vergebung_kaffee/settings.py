# versohnung_und_vergebung_kaffee/settings.py
from pathlib import Path
from email.utils import formataddr, parseaddr
from decouple import config
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")  # load .env into os.environ

# ── Core ───────────────────────────────────────────────────────────────────────
SECRET_KEY = config("SECRET_KEY", default="dev-secret-key-change-me")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "vv-kaffee-5b7b3eb05052.herokuapp.com"]

# Stripe (fail fast if missing in real envs)
STRIPE_PUBLISHABLE_KEY = config("STRIPE_PUBLISHABLE_KEY", default="")
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default="")
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET", default="")

SITE_URL = config("SITE_URL", default="http://127.0.0.1:8000")
SITE_NAME = config("SITE_NAME", default="Versöhnung und Vergebung Kaffee")

# ── Apps ──────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",

    "django.contrib.sites",        # required by allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",  # add other providers as needed
    "cloudinary_storage",          # optional, only if using Cloudinary
    "widget_tweaks",

    # project apps
    "products",
    "orders",
    "reviews",
    "profiles.apps.ProfilesConfig",
    "cart",
    "newsletter",
]

SITE_ID = 1

# ── Middleware ────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",  # keep after Auth

    # optional post-login middleware (only if you actually use it)
    "versohnung_und_vergebung_kaffee.middleware.fulfillment_redirect.FulfillmentPostLoginMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "versohnung_und_vergebung_kaffee.urls"

# ── Templates ─────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # global templates dir
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",  # required by allauth
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "cart.context_processors.cart_summary",
            ],
        },
    },
]

WSGI_APPLICATION = "versohnung_und_vergebung_kaffee.wsgi.application"

# ── Database ──────────────────────────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "OPTIONS": {"timeout": 20},
    }
}

DATABASE_URL = config("DATABASE_URL", default=None)
if DATABASE_URL:
    import dj_database_url
    DATABASES["default"] = dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        ssl_require=True,
    )

# ── Password validation ───────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ── I18N / TZ ─────────────────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True

# ── Static & Media ────────────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"}
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ── Optional Cloudinary (leave empty unless used) ─────────────────────────────
CLOUDINARY_URL = config("CLOUDINARY_URL", default="")

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# ── Email (Gmail SMTP) ────────────────────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
FROM_NAME = config("FROM_NAME", default=SITE_NAME)
_default_from_env = config("DEFAULT_FROM_EMAIL", default="")
_fallback_from = formataddr((FROM_NAME or "VV Kaffee", EMAIL_HOST_USER or "no-reply@vvk.com"))
if _default_from_env:
    parsed_name, parsed_addr = parseaddr(_default_from_env)
    DEFAULT_FROM_EMAIL = formataddr((parsed_name or FROM_NAME or "VV Kaffee", parsed_addr or EMAIL_HOST_USER or "no-reply@vvk.com"))
else:
    DEFAULT_FROM_EMAIL = _fallback_from
EMAIL_TIMEOUT = 20
ORDER_NOTIFICATION_EMAILS = config(
    "ORDER_NOTIFICATION_EMAILS",
    default="",
    cast=lambda v: [e.strip() for e in v.split(",") if e.strip()],
)

# ── Auth / Allauth ────────────────────────────────────────────────────────────
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Use username OR email to log in (new allauth style)
ACCOUNT_LOGIN_METHODS = {"username", "email"}

# Signup fields (asterisk means required)
ACCOUNT_SIGNUP_FIELDS = ["username*", "email*", "password1*", "password2*"]

# Email verification flow
ACCOUNT_EMAIL_VERIFICATION = "optional"  # consider "mandatory" in production

# Redirects
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/post-login/"   # our post-login router view
ACCOUNT_LOGOUT_ON_GET = True
LOGOUT_REDIRECT_URL = "/"             # take users to homepage after logout

# ── Logging ───────────────────────────────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "WARNING"},
}
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}



# ── Default PK type ───────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
