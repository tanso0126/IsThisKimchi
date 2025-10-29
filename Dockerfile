
# Python 3.11-slim 버전을 기반으로 시작해요.
FROM python:3.11-slim

# 작업 디렉토리를 만들어 줄게요.
WORKDIR /app

# 필요한 라이브러리부터 설치해요.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 게임 파일들을 전부 복사해요.
COPY . .

# 서버가 8080 포트를 사용한다고 알려줄게요.
EXPOSE 8080

# 마지막으로, 이 명령어로 게임을 실행시키는 거예요!
CMD ["python3", "main.py"]
