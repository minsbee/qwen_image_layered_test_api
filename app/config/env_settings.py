import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class EnvSettings:
    CURRENT_ENV = os.getenv("CURRENT_ENV")

    # Redis
    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = os.getenv("REDIS_PORT")
    REDIS_PRODUCT_DB = os.getenv("REDIS_PRODUCT_DB")
    REDIS_LOG_DB = os.getenv("REDIS_LOG_DB")

    if CURRENT_ENV == "development":
        REDIS_USER = os.getenv("REDIS_USER")
        REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
    else:
        REDIS_USER = None
        REDIS_PASSWORD = None

    # BackBlaze Cloud Storage(B2)
    B2_API_KEY_ID = os.getenv("B2_API_KEY_ID")
    B2_API_KEY = os.getenv("B2_API_KEY")
    B2_BUCKET_ID = os.getenv("B2_BUCKET_ID")

    # Logger
    LOG_LEVEL = os.getenv("LOG_LEVEL")

    # Openai
    OPENAI_PROJECT_ID = os.getenv("OPENAI_PROJECT_ID")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_LLM_MODEL = os.getenv("OPENAI_LLM_MODEL")
    OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL")


envs = EnvSettings()
