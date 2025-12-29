import os
import uuid
import torch
from PIL import Image
from typing import List, Tuple
from app.config import logger, envs
from app.config.model_config import (
    QWEN_MODEL_NAME,
    DEVICE,
    TORCH_DTYPE,
    USE_LIGHTNING_LORA,
    LIGHTNING_LORA_PATH
)


class ImageLayeredService:
    """이미지 레이어 분해 서비스"""

    def __init__(self):
        self.pipeline = None
        self.device = DEVICE
        self.output_dir = envs.OUTPUT_DIR or "outputs"
        os.makedirs(self.output_dir, exist_ok=True)

    async def load_model(self):
        """ML 모델 로딩"""
        try:
            from diffusers import QwenImageLayeredPipeline

            logger.info(f"Loading Qwen Image Layered model on device: {self.device}")
            logger.info(f"Using torch dtype: {TORCH_DTYPE}")

            # MPS/Apple Silicon은 bitsandbytes 미지원
            # CPU 모드로 로드 (메모리 부족 시 스왑 사용)
            logger.warning("⚠️  Apple Silicon detected - loading without quantization")
            logger.warning("⚠️  This will use ~60GB memory (may use swap)")

            self.pipeline = QwenImageLayeredPipeline.from_pretrained(
                QWEN_MODEL_NAME,
                torch_dtype=TORCH_DTYPE,
                low_cpu_mem_usage=True,
            )

            # CPU에서만 실행
            if self.device == "cpu":
                logger.info("Running on CPU (slow but works)")
            else:
                # MPS로 이동 시도 (메모리 부족할 수 있음)
                logger.info(f"Attempting to move to {self.device}...")
                try:
                    self.pipeline = self.pipeline.to(self.device)
                    logger.info(f"✅ Successfully moved to {self.device}")
                except Exception as e:
                    logger.error(f"Failed to move to {self.device}: {e}")
                    logger.warning("Falling back to CPU")
                    self.device = "cpu"

            # 선택: Lightning LoRA 로드
            if USE_LIGHTNING_LORA:
                self.pipeline.load_lora_weights(LIGHTNING_LORA_PATH)
                logger.info(f"Lightning LoRA loaded: {LIGHTNING_LORA_PATH}")

            logger.info("Model loaded successfully!")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    async def decompose_image(
        self,
        image: Image.Image,
        layers: int = 4,
        resolution: int = 640,
        num_inference_steps: int = 50,
        true_cfg_scale: float = 4.0,
        seed: int = 42
    ) -> Tuple[str, List[str], int]:
        """
        이미지를 여러 레이어로 분해

        Args:
            image: 입력 이미지
            layers: 생성할 레이어 수
            resolution: 출력 해상도
            num_inference_steps: 추론 스텝 수 (LoRA 사용 시 8)
            true_cfg_scale: CFG 스케일
            seed: 랜덤 시드

        Returns:
            (result_id, layer_paths, count)
        """
        if self.pipeline is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        try:
            # RGBA로 변환
            image = image.convert("RGBA")

            # 추론
            with torch.inference_mode():
                output = self.pipeline(
                    image=image,
                    layers=layers,
                    resolution=resolution,
                    num_inference_steps=num_inference_steps,
                    true_cfg_scale=true_cfg_scale,
                    generator=torch.Generator(device=self.device).manual_seed(seed)
                )

            # 결과 저장
            result_id = str(uuid.uuid4())[:8]
            paths = []

            for i, layer in enumerate(output.images[0]):
                filename = f"{result_id}_layer{i}.png"
                file_path = os.path.join(self.output_dir, filename)
                layer.save(file_path)
                paths.append(filename)
                logger.info(f"Saved layer {i} to {file_path}")

            return result_id, paths, len(paths)

        except Exception as e:
            logger.error(f"Image decomposition failed: {e}")
            raise

    def get_file_path(self, filename: str) -> str:
        """파일 경로 반환"""
        file_path = os.path.join(self.output_dir, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {filename}")
        return file_path


# 싱글톤 인스턴스
image_layered_service = ImageLayeredService()
