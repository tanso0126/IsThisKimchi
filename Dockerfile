# Python 3.11-slim 버전을 기반으로 시작해요.
FROM python:3.11-slim

# 작업 디렉토리를 만들어 줄게요.
WORKDIR /app

# 1. 먼저 의존성 파일만 복사하고 설치해요.
#    이렇게 하면, 코드만 바뀔 때는 이 레이어를 재사용해서 빌드 속도가 빨라져요.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. 이제 나머지 애플리케이션 코드를 복사해요.
#    .dockerignore 파일 덕분에 .env 같은 민감한 파일은 복사되지 않아요.
COPY . .

# 서버가 8080 포트를 사용한다고 알려줄게요.
# 실제로는 PORT 환경 변수로 포트를 지정할 수 있어요.
EXPOSE 8080

# 마지막으로, 이 명령어로 게임을 실행시키는 거예요!
# STORAGE_SECRET은 컨테이너 실행 시 환경 변수로 주입해줘야 해요.
CMD ["python3", "main.py"]