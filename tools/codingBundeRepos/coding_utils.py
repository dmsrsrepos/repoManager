import os
import logging
import http.client
import json
import socket
import time
import sys
from typing import Dict, Any, Tuple
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(".env.local"))
load_dotenv()

MAX_RETRIES = 3
RETRY_DELAY = 2  # 重试延迟（秒）
DEFAULT_TIMEOUT = 10  # 默认超时时间（秒）
MAX_TIMEOUT = 120  # 最大超时时间（秒）


def get_api_token() -> str:
    """从环境变量获取API令牌"""
    token = os.getenv("CODING_API_TOKEN")
    # print(token)
    return token


def handle_api_error(error_type: str, error: Exception) -> Dict[str, Any]:
    """统一处理API错误"""
    error_msg = str(error)
    logging.error("%s: %s", error_type, error_msg)
    return {"error": error_type, "message": error_msg}


def validate_id(id_value: Any, id_name="ID") -> bool:
    """验证ID是否有效"""
    return isinstance(id_value, int) and id_value > 0


def make_api_request(
    action: str, payload_data: Dict[str, Any] = None, timeout: int = 10
) -> Tuple[bool, Dict[str, Any]]:
    """
    发送API请求
    :param action: API动作名称
    :param payload_data: 请求负载数据
    :param timeout: 超时时间(秒)
    :return: (是否成功, 响应数据)
    """
    if not isinstance(timeout, int) or timeout < 1 or timeout > 30:
        timeout = 10

    if payload_data is None:
        payload_data = {}
    elif not isinstance(payload_data, dict):
        return False, handle_api_error(
            "INVALID_PAYLOAD", Exception("payload_data必须是字典")
        )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_api_token()}",
    }

    payload = json.dumps(payload_data)

    global cached_conn
    max_retries = 3
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            if not hasattr(sys, "cached_conn"):
                sys.cached_conn = http.client.HTTPSConnection(
                    "e.coding.net", timeout=timeout
                )
            conn = sys.cached_conn
            conn.request(
                "POST", f"/open-api/?action={action}", body=payload, headers=headers
            )

            response = conn.getresponse()
            data = response.read()

            if response.status != 200:
                return False, handle_api_error(
                    "HTTP_ERROR",
                    Exception(f"HTTP {response.status}: {response.reason}"),
                )

            response_data = json.loads(data.decode("utf-8"))

            if "Response" in response_data and "Error" in response_data["Response"]:
                error = response_data["Response"]["Error"]
                return False, handle_api_error(
                    error.get("Code", "API_ERROR"),
                    Exception(error.get("Message", "Unknown API error")),
                )

            return True, response_data

        except (http.client.HTTPException, socket.timeout, ConnectionError) as e:
            if attempt == max_retries - 1:
                return False, handle_api_error("NETWORK_ERROR", e)
            time.sleep(retry_delay)

        except json.JSONDecodeError as e:
            return False, handle_api_error("JSON_PARSE_ERROR", e)

        except Exception as e:
            return False, handle_api_error("UNKNOWN_ERROR", e)

    return False, handle_api_error(
        "MAX_RETRIES_EXCEEDED", Exception(f"请求失败，已达到最大重试次数{max_retries}")
    )
