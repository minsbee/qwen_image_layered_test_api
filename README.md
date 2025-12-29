# Qwen Image Layered API

Qwen-Image-Layered 모델을 활용한 이미지 레이어 분해 API 서버입니다.

## 프로젝트 개요

이 프로젝트는 Alibaba의 Qwen-Image-Layered 모델을 FastAPI 기반 API 서버로 제공합니다. 입력된 이미지를 여러 개의 RGBA 레이어로 분해하여 각 레이어를 독립적으로 편집할 수 있게 합니다. 레이어드 아키텍처를 적용하여 확장 가능하고 유지보수하기 쉬운 구조로 설계되었습니다.

## 주요 기능

- **이미지 레이어 분해**: 하나의 이미지를 여러 RGBA 레이어로 자동 분해
- **레이어드 아키텍처**: Router, Service, Config 계층 분리
- **디바이스 자동 감지**: CUDA, MPS, CPU 자동 선택
- **환경 설정 관리**: 개발/프로덕션 환경별 설정
- **Redis 캐싱**: 데이터 캐싱 및 세션 관리
- **RabbitMQ 메시지 큐**: 비동기 작업 처리
- **OpenAI API 통합**: AI 기능 확장
- **코드 품질 관리**: pre-commit, Ruff를 통한 코드 포맷팅 및 린팅

## 기술 스택

### Backend
- **FastAPI**: 고성능 비동기 API 프레임워크
- **Uvicorn**: ASGI 서버

### ML/AI
- **PyTorch**: 딥러닝 프레임워크
- **Diffusers**: Hugging Face Diffusion 모델 라이브러리
- **Transformers**: Hugging Face Transformers 라이브러리
- **Qwen-Image-Layered**: 이미지 레이어 분해 모델

### Infrastructure
- **Redis**: 캐싱 및 세션 관리
- **RabbitMQ (aio-pika)**: 메시지 큐
- **Docker**: 컨테이너화
- **OpenAI API**: AI 기능 통합

### Development Tools
- **Ruff**: 코드 포맷팅 및 린팅
- **pre-commit**: Git 훅 관리
- **invoke**: 태스크 실행 도구

## 프로젝트 구조

```
.
├── app/
│   ├── config/
│   │   ├── env_settings.py      # 환경 변수 설정
│   │   ├── model_config.py      # ML 모델 설정
│   │   ├── exceptions.py        # 예외 처리
│   │   ├── logger.py            # 로깅 설정
│   │   └── redis_client.py      # Redis 클라이언트
│   ├── routers/
│   │   ├── bucket.py            # B2 스토리지 API
│   │   └── image_layered.py     # 이미지 레이어 분해 API ⭐
│   ├── services/
│   │   ├── bucket_service.py    # B2 스토리지 서비스
│   │   └── image_layered_service.py  # 이미지 레이어 분해 서비스 ⭐
│   ├── __init__.py
│   └── main.py                  # 애플리케이션 진입점
├── outputs/                     # 생성된 레이어 이미지 저장
├── .env                         # 프로덕션 환경 변수
├── .env.dev                     # 개발 환경 변수
├── requirements.txt             # 의존성 패키지
└── tasks.py                     # Invoke 태스크
```

## 설치 및 실행 방법

### 요구 사항

- Python 3.12 이상
- **GPU 권장**: NVIDIA GPU (CUDA) 또는 Apple Silicon (MPS)
- **메모리**: 최소 64GB RAM 권장 (양자화 사용 시 16GB+)
- Docker (선택 사항)

### 로컬 개발 환경 설정

```bash
# 저장소 클론
git clone https://github.com/your-username/qwen_image_layered_test_api.git
cd qwen_image_layered_test_api

# 가상 환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# torchvision 설치 (추가)
pip install torchvision

# 개발 모드 실행
invoke dev
```

### 환경 변수 설정

`.env.dev` 또는 `.env` 파일에 필요한 환경 변수를 설정합니다:

```env
# 기본 설정
CURRENT_ENV=development
LOG_LEVEL=DEBUG

# Image Layered 설정
OUTPUT_DIR=outputs
ENABLE_ML_MODEL=true  # false로 설정 시 모델 로딩 안 함

# Redis 설정
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PRODUCT_DB=10
REDIS_LOG_DB=1

# B2 스토리지 설정 (선택 사항)
B2_API_KEY_ID=your_key_id
B2_API_KEY=your_key
B2_BUCKET_ID=your_bucket_id

# OpenAI 설정 (선택 사항)
OPENAI_API_KEY=your_openai_api_key
OPENAI_LLM_MODEL=gpt-4
```

## 실행 명령어

```bash
invoke dev      # 개발 모드 실행
invoke start    # 프로덕션 모드 실행
invoke lint     # 코드 린팅
invoke format   # 코드 포맷팅
```

## API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API 엔드포인트

### 이미지 레이어 분해

**POST** `/api/image/decompose`

이미지를 여러 RGBA 레이어로 분해합니다.

**Parameters:**
- `file` (UploadFile): 분해할 이미지 파일
- `layers` (int, optional): 생성할 레이어 수 (기본값: 4, 범위: 2-10)
- `resolution` (int, optional): 출력 해상도 (기본값: 640)
- `num_inference_steps` (int, optional): 추론 스텝 수 (기본값: 50)
- `true_cfg_scale` (float, optional): CFG 스케일 (기본값: 4.0)
- `seed` (int, optional): 랜덤 시드 (기본값: 42)

**Response:**
```json
{
  "success": true,
  "id": "abc12345",
  "layers": [
    "abc12345_layer0.png",
    "abc12345_layer1.png",
    "abc12345_layer2.png",
    "abc12345_layer3.png"
  ],
  "count": 4,
  "message": "Successfully decomposed into 4 layers"
}
```

### 레이어 파일 다운로드

**GET** `/api/image/files/{filename}`

생성된 레이어 이미지 파일을 다운로드합니다.

### 기타 엔드포인트

- `GET /`: 서버 상태 확인
- `GET /api/authorize-b2`: B2 스토리지 인증
- `GET /api/get-upload-url-b2`: B2 업로드 URL 획득

## 사용 예시

### cURL

```bash
# 이미지 분해
curl -X POST "http://localhost:8000/api/image/decompose?layers=4" \
  -F "file=@your_image.png"

# 레이어 다운로드
curl "http://localhost:8000/api/image/files/abc12345_layer0.png" \
  --output layer0.png
```

### Python

```python
import requests

# 이미지 분해
with open("image.png", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/image/decompose",
        files={"file": f},
        params={"layers": 4}
    )

result = response.json()
print(f"Generated {result['count']} layers")

# 레이어 다운로드
for layer_file in result["layers"]:
    layer_response = requests.get(
        f"http://localhost:8000/api/image/files/{layer_file}"
    )
    with open(layer_file, "wb") as f:
        f.write(layer_response.content)
```

## ⚠️ 중요 사항

### 모델 크기 및 메모리 요구사항

- **모델 크기**: 57.7GB
- **필요 메모리**:
  - 원본 모델: 60GB+ RAM
  - 양자화 모델: 16GB+ RAM (현재 미지원)

### GPU 요구사항

**지원 환경:**
- ✅ NVIDIA GPU (CUDA): A100 80GB, H100 80GB 권장
- ⚠️ Apple Silicon (MPS): 메모리 부족으로 실행 어려움
- ⚠️ CPU: 매우 느림, 실용성 낮음

**일반 소비자용 GPU로는 실행이 어렵습니다:**
- RTX 4090 (24GB): ❌ 메모리 부족
- RTX 4080 (16GB): ❌ 메모리 부족
- RTX 4070 (12GB): ❌ 메모리 부족

### 권장 사항

개인 PC에서는 다음 대안을 고려하세요:
1. **Hugging Face Inference API**: 서버에서 모델 실행
2. **클라우드 GPU 렌탈**: AWS SageMaker, RunPod, Lambda Labs 등
3. **경량 모델 대기**: 향후 출시될 작은 버전 대기

## 개발 모드에서 모델 로딩 비활성화

모델 없이 API 서버만 테스트하려면:

```env
# .env.dev
ENABLE_ML_MODEL=false
```

## 라이센스

이 프로젝트는 MIT 라이센스에 따라 배포됩니다.

## 참고 자료

- [Qwen-Image-Layered Model Card](https://huggingface.co/Qwen/Qwen-Image-Layered)
- [Qwen-Image-Layered GitHub](https://github.com/QwenLM/Qwen-Image-Layered)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Diffusers Documentation](https://huggingface.co/docs/diffusers)
