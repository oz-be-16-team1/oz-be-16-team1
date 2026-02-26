from .base import *  # noqa: F403
import environ

DEBUG = False

# BASE_DIR은 base.py에 정의되어 있지만, 린터 에러 방지를 위해
env = environ.Env

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["mydomain.com"])  # noqa: F405

# 배포용 DB (PostgreSQL)
DATABASES = {
    "default": env.db(
        "DATABASE_URL"  # noqa: F405
    )  # .env에 DATABASE_URL=postgres://user:pw@host:port/dbname 형식으로 저장
}

# 정적 파일 설정
STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405
MEDIA_ROOT = BASE_DIR / "media"  # noqa: F405


# 보안 관련 설정
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)  # Load Balancer 사용 시 필수
CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in ALLOWED_HOSTS]
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
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
