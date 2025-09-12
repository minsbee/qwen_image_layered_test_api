import sys
import time
import asyncio
import threading
import requests
from loguru import logger
from urllib.parse import quote
from datetime import datetime
from zoneinfo import ZoneInfo
from .env_settings import envs

# 현재 환경 구분
current_env = envs.CURRENT_ENV

# 로그 정의
LOG_LEVEL = envs.LOG_LEVEL or "INFO"

# 한국 기준 시간 정의
kst_now = datetime.now(ZoneInfo("Asia/Seoul"))


def kst_log_format(record):
    kst_time = record["time"].astimezone(ZoneInfo("Asia/Seoul"))
    formatted_time = kst_time.strftime("%Y-%m-%d %H:%M:%S")
    level = record["level"].name
    # 로거의 메시지가 중괄호(ex: 객체 등)로 전달되는 경우 플레이스 홀더로 해석하는 것을 방지
    message = record["message"].replace("{", "{{").replace("}", "}}")

    return f"{formatted_time} | {level} | {message}\n"


def dev_log_format(record):
    kst_time = record["time"].astimezone(ZoneInfo("Asia/Seoul"))
    formatted_time = kst_time.strftime("%Y-%m-%d %H:%M:%S")
    level = record["level"].name
    message = record["message"].replace("{", "{{").replace("}", "}}")

    return f"{formatted_time} | <level>{level}</level> | {message}\n"


# 기본 핸들러 제거
logger.remove()

# 로그 레벨별 색상 커스터마이징
logger.level("DEBUG", color="<cyan>")
logger.level("INFO", color="<green>")
logger.level("WARNING", color="<yellow>")
logger.level("ERROR", color="<red><bold>")
logger.level("CRITICAL", color="<magenta><bold>")

# 기본 핸들러 추가(개발 환경 가정)
logger.add(
    sys.stdout,
    level=LOG_LEVEL.upper(),
    format=dev_log_format,
    colorize=True,
    enqueue=False,  # 동기 처리로 변경
)


# Redis 저장 함수
async def save_redis_log(message):
    from .redis_client import redis_log_client

    record = message.record
    log_entry = kst_log_format(record)
    await redis_log_client.rpush("log_entries", log_entry)


# production 환경인 경우에만 로그를 B2 버킷에 업로드
if current_env == "production":
    logger.add(
        save_redis_log,
        level=LOG_LEVEL.upper(),
        colorize=True,
        enqueue=False,  # 동기 처리로 변경
    )

    # 동기 함수로 구현하여 이벤트 루프 문제 해결
    def flush_logs_to_b2_sync():
        import redis.asyncio as redis
        from app.services import get_upload_url_b2

        # logger 저장용 redis 클라이언트 생성
        redis_log_client = redis.Redis(
            host=envs.REDIS_HOST,
            port=envs.REDIS_PORT,
            db=envs.REDIS_LOG_DB,
            username=envs.REDIS_USER if current_env == "development" else None,
            password=envs.REDIS_PASSWORD
            if current_env == "development"
            else None,
        )

        # 새 이벤트 루프 생성 및 실행
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # 상태 별 redis 키 이름 설정
        main_key = "log_entries"
        pending_key = "log_entries:pending"

        try:
            # 원자적으로 기존 로그 pending으로 이동
            exists_future = redis_log_client.exists(main_key)
            exists = loop.run_until_complete(exists_future)
            if exists:
                # RENAME은 원자적(키가 없으면 에러나므로 존재할 때만 진행)
                rename_future = redis_log_client.rename(main_key, pending_key)
                loop.run_until_complete(rename_future)
            else:
                logger.warning("⚠️ 업로드 할 로그 데이터가 없습니다.")
                return

            # pending 키에서 모든 로그 읽기
            get_logs_future = redis_log_client.lrange(pending_key, 0, -1)
            log_entries = loop.run_until_complete(get_logs_future)
            logs = (
                [entry.decode("utf-8") for entry in log_entries]
                if log_entries
                else []
            )

            if not logs:
                logger.warning("⚠️ 업로드할 로그 데이터가 없습니다.")
                loop.run_until_complete(redis_log_client.delete(pending_key))
                return

            # 로그 내용 구성
            content = "".join(logs)
            current_kst = datetime.now(ZoneInfo("Asia/Seoul"))

            # B2 업로드 URL 가져오기
            upload_info = loop.run_until_complete(get_upload_url_b2())
            if not upload_info:
                logger.error("❌ B2 업로드 URL 정보를 얻지 못했습니다.")
                raise Exception("B2 업로드 URL 정보를 얻지 못했습니다.")

            upload_url = upload_info.get("uploadUrl")
            token = upload_info.get("authorizationToken")

            # 파일 이름 설정
            file_name = quote(
                "logs/PRODUCT_RECOMMEND_{}.log".format(
                    current_kst.strftime("%Y%m%d%H%M%S")
                )
            )
            headers = {
                "Authorization": token,
                "Content-Type": "text/plain; charset=utf-8",
                "X-Bz-File-Name": file_name,
                "X-Bz-Content-Sha1": "do_not_verify",
            }

            # B2에 업로드
            response = requests.post(
                upload_url, data=content.encode("utf-8"), headers=headers
            )

            response.raise_for_status()
            logger.info("✅ 로그가 성공적으로 B2에 업로드되었습니다.")

            # 업로드 성공 시 pending 로그 삭제
            loop.run_until_complete(redis_log_client.delete(pending_key))
            logger.info("🗑️ 임시 저장된 로그가 성공적으로 제거되었습니다.")

        except Exception as e:
            logger.error("❌ 로그 플러시 중 예외 발생: " + str(e))
            # 업로드 실패 시, pending 로그들을 메인 키로 복구하는 원자적 Lua 스크립트 실행
            try:
                lua_script = """
                            local pending = KEYS[1]
                            local main = KEYS[2]
                            local logs = redis.call('LRANGE', pending, 0, -1)
                            if #logs > 0 then
                                for i=1, #logs do
                                    redis.call('RPUSH', main, logs[i])
                                end
                            end
                            return redis.call('DEL', pending)
                            """
                restore_script = redis_log_client.register_script(lua_script)
                loop.run_until_complete(
                    restore_script(keys=[pending_key, main_key])
                )

                logger.info("❗️업로드 실패로 인한 로그 복구 완료")
            except Exception as restore_err:
                logger.error("❌ 로그 복구 중 예외 발생: " + str(restore_err))
        finally:
            # Redis 연결 종료 및 이벤트 루프 닫기
            close_future = redis_log_client.close()
            loop.run_until_complete(close_future)
            loop.close()

    def automate_log_flush(interval):
        while True:
            time.sleep(interval)
            try:
                flush_logs_to_b2_sync()
            except Exception as e:
                logger.error("❌ 로그 플러시 자동화 중 예외 발생: " + str(e))

    # 자동 로그 플러시 (1시간 마다 한 번씩 업로드)
    flush_thread = threading.Thread(
        target=automate_log_flush, args=(60 * 60,), daemon=True
    )
    flush_thread.start()

    # 세팅 확인을 위한 테스트 로그 (원하는 경우 주석 해제)
    # logger.debug("This is a DEBUG message")
    # logger.info("This is an INFO message")
    # logger.warning("This is a WARNING message")
    # logger.error("This is an ERROR message")
    # logger.critical("This is a CRITICAL message")
