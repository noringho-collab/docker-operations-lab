# Python이 설치된 기본 이미지 사용
FROM python:3.12-slim

# 컨테이너 내부 작업 폴더 지정
WORKDIR /app

# 패키지 목록을 복사하고 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 작성한 API 코드 복사
COPY main.py .

# 컨테이너 시작 시 웹 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
