import redis.asyncio as redis
from app.config import envs

current_env = envs.CURRENT_ENV

# Redis 클라이언트 설정 (비동기)
redis_log_client = redis.Redis(
    host=envs.REDIS_HOST,
    port=envs.REDIS_PORT,
    db=envs.REDIS_LOG_DB,
    username=envs.REDIS_USER if current_env == "development" else None,
    password=envs.REDIS_PASSWORD if current_env == "development" else None,
)
