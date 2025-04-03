from fastapi import APIRouter
from app.services import authorize_b2, get_upload_url_b2

router = APIRouter()


@router.get("/authorize-b2")
async def authorize_b2_api():
    authorize_result = await authorize_b2()

    return {"message": authorize_result}


@router.get("/get-upload-url-b2")
async def get_upload_url_b2_api():
    upload_url = await get_upload_url_b2()
    if upload_url:
        return {"message": upload_url}
    else:
        return {"message": "No upload url found"}
