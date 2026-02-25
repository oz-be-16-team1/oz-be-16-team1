from pathlib import Path  # 추가: F405 해결
from datetime import timedelta
from .base import *  # noqa: F403
import os
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # noqa: F405
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))
AUTH_USER_MODEL = "users.User"

DEBUG = env.bool("DEBUG", default=True)

# .env에서 가져오거나 기본값 설정
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "web"])

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB"),  # .env의 POSTGRES_DB 사용
        "USER": env("POSTGRES_USER"),  # .env의 POSTGRES_USER 사용
        "PASSWORD": env("POSTGRES_PASSWORD"),  # .env의 POSTGRES_PASSWORD 사용
        "HOST": env("DB_HOST", default="db"),
        "PORT": env("DB_PORT", default="5432"),
    }
}

# 로깅 설정 (기존 내용 유지)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "theoriginaldongik@gmail.com"
EMAIL_HOST_PASSWORD = "tfsnprdvhhxrflph"  # 일반 비번이 아닌 '앱 비밀번호'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# 로그인 성공 시 이동할 페이지 (메인 페이지)
LOGIN_REDIRECT_URL = "users:main"

# 로그아웃 성공 시 이동할 페이지 (로그인 페이지)
LOGOUT_REDIRECT_URL = "/login/"

# 개발 환경에서는 쿠키 secure 설정을 끔
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,  # noqa: F405
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
}
