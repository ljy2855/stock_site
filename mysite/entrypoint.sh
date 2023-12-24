#!/bin/bash

# 데이터베이스 마이그레이션 실행
python manage.py migrate --noinput

# 정적 파일 수집
python manage.py collectstatic --noinput

# Gunicorn을 사용하여 Django 앱 실행
gunicorn mysite.wsgi:application --bind 0.0.0.0:8000