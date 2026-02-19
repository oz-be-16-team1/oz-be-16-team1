from .base import *
import os
import environ
env = environ.Env()

DEBUG = env.bool("DEBUG", default=True)

# .env에서 가져오거나 기본값 설정
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "web"])

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB"),        # .env의 POSTGRES_DB 사용
        "USER": env("POSTGRES_USER"),      # .env의 POSTGRES_USER 사용
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