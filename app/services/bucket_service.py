import base64
import requests
from app.config import envs, logger

B2_API_KEY_ID = envs.B2_API_KEY_ID
B2_API_KEY = envs.B2_API_KEY
B2_BUCKET_ID = envs.B2_BUCKET_ID


async def authorize_b2():
    try:
        url = "https://api.backblaze.com/b2api/v3/b2_authorize_account"
        headers = {
            "Authorization": f"Basic {base64.b64encode(f'{B2_API_KEY_ID}:{B2_API_KEY}'.encode()).decode()}"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        logger.error(f"❌ 인증 실패: {e}")


async def get_upload_url_b2():
    try:
        authorize_result = await authorize_b2()
        api_url = authorize_result["apiInfo"]["storageApi"]["apiUrl"]
        token = authorize_result["authorizationToken"]
        url = f"{api_url}/b2api/v3/b2_get_upload_url?bucketId={B2_BUCKET_ID}"
        headers = {
            "Authorization": token,
            "Content-Type": "application/json",
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        logger.error(f"❌ 전송 url 호출 실패: {e}")
