# 1. 파이썬 베이스 이미지 설정
FROM python:3.13-slim

# uv 설치
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 2. 파이썬 관련 환경 변수 설정
# .pyc 파일을 생성하지 않음
ENV PYTHONDONTWRITEBYTECODE=1
# 로그가 버퍼링 없이 즉시 출력되도록 설정
ENV PYTHONUNBUFFERED=1
# uv가 가상환경을 만들지 않고 시스템에 직접 설치하도록 설정
ENV UV_SYSTEM_PYTHON=1

# 3. 작업 디렉토리 설정
WORKDIR /app

# 4. 의존성 파일 복사 및 설치 (캐싱 활용)
# 소스 코드 전체를 복사하기 전에 lock 파일만 먼저 복사해서 설치해야 빌드 속도가 빨라집니다.
COPY pyproject.toml uv.lock /app/

# 5. 의존성 설치 (시스템 파이썬에 동기화)
RUN uv sync --frozen --no-install-project

# 6. 프로젝트 전체 파일 복사 (단, .dockerignore 설정 권장)
COPY . /app/

# 7. scripts 폴더 복사 및 권한 부여
# (compose에서 /scripts/run.sh를 실행하므로 경로를 맞춰줍니다)
COPY scripts/ /scripts/
RUN chmod +x /scripts/run.sh

# 8. 포트 노출 (Django 기본 포트)
EXPOSE 8000