"""ML 모델 설정"""
import torch

# Qwen Image Layered 모델 설정
QWEN_MODEL_NAME = "Qwen/Qwen-Image-Layered"

# Lightning LoRA 설정 (선택사항)
USE_LIGHTNING_LORA = False
LIGHTNING_LORA_PATH = "Qwen-Image-Lightning-8steps-V1.1.safetensors"

# 기본 추론 파라미터
DEFAULT_LAYERS = 4
DEFAULT_RESOLUTION = 640
DEFAULT_NUM_INFERENCE_STEPS = 50  # Lightning LoRA 사용 시 8로 변경
DEFAULT_TRUE_CFG_SCALE = 4.0
DEFAULT_SEED = 42


def get_device():
    """사용 가능한 디바이스 자동 감지"""
    if torch.cuda.is_available():
        return "cuda"
    # MPS는 메모리 부족으로 비활성화
    # elif torch.backends.mps.is_available():
    #     return "mps"  # Apple Silicon (M1/M2/M3)
    else:
        return "cpu"  # 57.7GB 모델은 CPU만 가능 (36GB 메모리)


def get_torch_dtype(device: str):
    """디바이스에 맞는 torch dtype 반환"""
    if device == "cuda":
        return torch.bfloat16
    elif device == "mps":
        return torch.float16  # MPS는 bfloat16을 아직 완전히 지원하지 않을 수 있음
    else:
        return torch.float32  # CPU는 float32가 안전


# GPU 설정
DEVICE = get_device()
TORCH_DTYPE = get_torch_dtype(DEVICE)
