from fastapi import APIRouter, UploadFile, File, Query
from fastapi.responses import FileResponse
from PIL import Image
import io
from app.services.image_layered_service import image_layered_service
from app.config import logger

router = APIRouter()


@router.post("/decompose")
async def decompose_image(
    file: UploadFile = File(..., description="업로드할 이미지 파일"),
    layers: int = Query(default=4, ge=2, le=10, description="생성할 레이어 수"),
    resolution: int = Query(default=640, ge=256, le=2048, description="출력 해상도"),
    num_inference_steps: int = Query(default=50, ge=1, le=100, description="추론 스텝 수"),
    true_cfg_scale: float = Query(default=4.0, ge=1.0, le=10.0, description="CFG 스케일"),
    seed: int = Query(default=42, description="랜덤 시드")
):
    """
    이미지를 여러 레이어로 분해합니다.

    - **file**: 분해할 이미지 파일 (JPEG, PNG 등)
    - **layers**: 생성할 레이어 수 (2-10)
    - **resolution**: 출력 해상도 (256-2048)
    - **num_inference_steps**: 추론 스텝 수 (Lightning LoRA 사용 시 8 권장)
    - **true_cfg_scale**: CFG 스케일 값
    - **seed**: 재현성을 위한 랜덤 시드
    """
    try:
        # 이미지 읽기
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))

        logger.info(f"Processing image: {file.filename}, layers: {layers}")

        # 이미지 분해
        result_id, layer_paths, count = await image_layered_service.decompose_image(
            image=image,
            layers=layers,
            resolution=resolution,
            num_inference_steps=num_inference_steps,
            true_cfg_scale=true_cfg_scale,
            seed=seed
        )

        return {
            "success": True,
            "id": result_id,
            "layers": layer_paths,
            "count": count,
            "message": f"Successfully decomposed into {count} layers"
        }

    except Exception as e:
        logger.error(f"Decompose error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/files/{filename}")
async def get_layer_file(filename: str):
    """
    생성된 레이어 이미지 파일을 다운로드합니다.

    - **filename**: 레이어 파일명 (예: abc12345_layer0.png)
    """
    try:
        file_path = image_layered_service.get_file_path(filename)
        return FileResponse(
            file_path,
            media_type="image/png",
            filename=filename
        )
    except FileNotFoundError as e:
        logger.error(f"File not found: {filename}")
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"Error serving file: {e}")
        return {
            "success": False,
            "error": str(e)
        }
