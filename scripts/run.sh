#!/bin/sh
# 에러 발생 시 즉시 중단
set -e

echo "Wait for DB..."
# DB가 준비될 때까지 기다리는 로직이 있으면 좋지만, 없으면 일단 진행
python manage.py makemigrations
echo "--- Apply Database Migrations ---"
python manage.py migrate

echo "Starting Server..."
# 개발 환경(dev)이라면 아래 명령어를 추천 (코드 수정 시 자동 재시작됨)
#python manage.py runserver 0.0.0.0:8000

#Swagger UI용 CSS/JS 파일들이 한곳에 모여 화면이 깨지지 않고 잘 나오게
python manage.py collectstatic --noinput

# 만약 운영 환경이라서 꼭 gunicorn을 써야 한다면 아래 주석 해제
 gunicorn --bind 0.0.0.0:8000 config.wsgi:application --workers 2
