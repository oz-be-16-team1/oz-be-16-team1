from .base import *

# import environ      # docker-compose에서 주입된 .env 읽기
# env = environ.Env()
# environ.Env.read_env()  # docker-compose에서 주입된 .env 읽기

DEBUG = False
ALLOWED_HOSTS = ["mydomain.com"]  # 실제 도메인/IP

# 배포용 DB (Postgres/MySQL 등)
DATABASES = {
    # "default": env.db(),  # DATABASE_URL 환경변수 사용
}

# 보안 관련 설정
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# 로깅은 에러 중심으로
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "ERROR",
    },
}
