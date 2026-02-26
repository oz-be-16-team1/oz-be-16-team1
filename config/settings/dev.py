from pathlib import Path  # 추가: F405 해결
from .base import *  # noqa: F403
import os
import sys
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

LOGIN_URL = "users:login"

# 로그인 성공 시 이동할 페이지 (메인 페이지)
LOGIN_REDIRECT_URL = "users:main"

# 로그아웃 성공 시 이동할 페이지 (로그인 페이지)
LOGOUT_REDIRECT_URL = "/login/"


# 테스트 환경에서 마이그레이션 파일을 일일이 읽지 않고 모델 구조대로 테이블을 생성하게
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATIONS_MODULES = {
    "users": None,
    "token_blacklist": None,
}
# 테스트 실행 중일 때만 SQLite 사용
if "test" in sys.argv:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
