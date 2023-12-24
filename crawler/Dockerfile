# Python 이미지를 기반으로 설정
FROM python:3.9.18

# 작업 디렉토리 설정
WORKDIR /usr/src/app

# 의존성 파일 복사
COPY requirements.txt ./

# 필요한 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 파일 복사
COPY . .

# Scrapyd 서비스 실행
CMD ["scrapyd"]