# 1. 빌드 스테이지
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. 실행 스테이지
FROM python:3.12-slim
WORKDIR /app
# 필요한 파일 복사 및 권한 설정
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .

# 포트 노출
EXPOSE 8000

# 실행 스크립트에 실행 권한 부여
RUN chmod +x start.sh


# 컨테이너 시작 시 실행될 명령
CMD ["sh", "start.sh"]
