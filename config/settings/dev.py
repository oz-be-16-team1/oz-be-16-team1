from pathlib import Path  # 추가: F405 해결
from .base import *  # noqa: F403
import os
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # noqa: F405
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

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
EMAIL_HOST_USER = "자신의_구글_이메일@gmail.com"
EMAIL_HOST_PASSWORD = "구글_앱_비밀번호"  # 일반 비번이 아닌 '앱 비밀번호' 발급 필요
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
