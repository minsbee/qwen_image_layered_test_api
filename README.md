# FastAPI 보일러플레이트

AI 관련 미니 프로젝트를 빠르게 개발하기 위한 FastAPI 기반 보일러플레이트입니다.

## 프로젝트 개요

이 보일러플레이트는 AI 프로젝트를 위한 기본적인 백엔드 API 서버 구조를 제공합니다. FastAPI 프레임워크를 기반으로 하여 빠른 API 개발, 자동 문서화, 타입 힌트 등의 기능을 제공하며, 개발 및 배포 환경 설정이 미리 구성되어 있습니다.

## 주요 기능

- **FastAPI 기반 API 서버**: 고성능 비동기 API 서버 구조
- **환경 설정 관리**: 개발/프로덕션 환경에 따른 설정 관리
- **로깅 시스템**: 로깅 설정 및 로그 저장 기능
- **예외 처리**: 글로벌 예외 핸들러 설정
- **B2 스토리지 연동**: 파일 저장 기능
- **Docker 지원**: 개발 및 배포를 위한 Docker 설정
- **코드 품질 관리**: pre-commit, Ruff를 통한 코드 포맷팅 및 린팅

## 기술 스택

- **Backend**: FastAPI
- **서버 실행**: Uvicorn
- **패키지 관리**: pip
- **환경 변수 관리**: python-dotenv
- **태스크 실행**: invoke
- **컨테이너화**: Docker
- **캐싱**: Redis
- **코드 포맷팅/린팅**: Ruff, pre-commit

## 프로젝트 구조

```
.
├── app/                    # 애플리케이션 코드
│   ├── config/             # 환경 설정 및 로깅 설정
│   │   ├── env_settings.py # 환경 변수 설정
│   │   ├── exceptions.py   # 예외 처리 설정
│   │   ├── logger.py       # 로깅 설정
│   │   └── redis_client.py # Redis 클라이언트 설정
│   ├── routers/            # API 라우터
│   │   └── bucket.py       # B2 저장소 관련 API
│   ├── services/           # 비즈니스 로직
│   │   └── bucket_service.py # B2 저장소 관련 서비스
│   ├── __init__.py         # 애플리케이션 초기화
│   └── main.py             # 애플리케이션 진입점
├── public/                 # 정적 파일
├── test/                   # 테스트 코드
├── .dockerignore           # Docker 무시 파일 설정
├── .env                    # 프로덕션 환경 변수
├── .env.dev                # 개발 환경 변수
├── .gitignore              # Git 무시 파일 설정
├── .pre-commit-config.yaml # pre-commit 설정
├── Dockerfile              # Docker 빌드 설정
├── README.md               # 프로젝트 문서
├── pyproject.toml          # Python 프로젝트 설정
├── requirements.txt        # 의존성 패키지 목록
├── start.sh                # 실행 스크립트
└── tasks.py                # Invoke 태스크 정의
```

## 설치 및 실행 방법

### 요구 사항

- Python 3.9 이상
- Docker (선택 사항)

### 로컬 개발 환경 설정

```bash
# 저장소 클론
git clone https://github.com/your-username/fastapi_custom_boiler_plate.git
cd fastapi_custom_boiler_plate

# 가상 환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 개발 모드 실행
invoke dev
```

### 환경 변수 설정

`.env.dev` 또는 `.env` 파일에 필요한 환경 변수를 설정합니다:

```
# 기본 설정
CURRENT_ENV=development  # development 또는 production
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# B2 스토리지 설정 (선택 사항)
B2_APPLICATION_KEY_ID=your_key_id
B2_APPLICATION_KEY=your_key
B2_BUCKET_NAME=your_bucket_name

# Redis 설정 (선택 사항)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

### Docker로 실행

```bash
# Docker 이미지 빌드
docker build -t fastapi-boilerplate .

# Docker 컨테이너 실행
docker run -p 8000:8000 --env-file .env fastapi-boilerplate
```

## 실행 명령어

이 프로젝트는 invoke 라이브러리를 사용하여 주요 명령어를 관리합니다:

- `invoke dev`: 개발 모드 실행 (.env.dev 환경 변수 적용, DEBUG 로깅)
- `invoke start`: 프로덕션 모드 실행 (.env 환경 변수 적용, INFO 로깅)
- `invoke lint`: Ruff 린터로 코드 검사
- `invoke format`: Ruff로 코드 포맷팅
- `invoke test`: pytest로 테스트 실행

## API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 주요 API 엔드포인트

- `GET /`: 기본 라우트, 서버 상태 확인
- `GET /api/authorize-b2`: B2 스토리지 인증
- `GET /api/get-upload-url-b2`: B2 업로드 URL 획득

## 커스터마이징 가이드

1. 새로운 라우터 추가:
   - `app/routers/` 디렉토리에 새 라우터 파일 생성
   - `app/__init__.py`에 라우터 등록

2. 서비스 추가:
   - `app/services/` 디렉토리에 새 서비스 파일 생성
   - 필요한 경우 `app/services/__init__.py`에 가져오기 설정

3. 환경 변수 추가:
   - `app/config/env_settings.py`에 새 환경 변수 추가
   - `.env` 및 `.env.dev` 파일에 해당 변수 설정

## 프로젝트 확장

이 보일러플레이트는 다음과 같은 확장이 가능합니다:

- **데이터베이스 연동**: SQLAlchemy, MongoDB 등 추가
- **인증 시스템**: JWT, OAuth 등 추가
- **백그라운드 작업**: Celery, FastAPI Background Tasks 등 추가
- **캐싱 확장**: Redis 캐싱 시스템 확장
- **AI 모델 통합**: 머신러닝/딥러닝 모델 통합

## 기여 가이드

1. 이 저장소를 포크하고 기능 브랜치를 생성합니다.
2. 변경 사항을 커밋하고 브랜치에 푸시합니다.
3. 풀 리퀘스트를 생성합니다.

## 라이센스

이 프로젝트는 MIT 라이센스에 따라 배포됩니다.
