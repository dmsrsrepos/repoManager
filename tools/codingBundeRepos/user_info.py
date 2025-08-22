from typing import Dict, Any
from utils import handle_api_error, make_api_request


def _user_info(user_info: Dict[str, Any]) -> bool:
    required_fields = ["Id", "Name"]
    return all(field in user_info for field in required_fields)


def fetch_coding_user_info() -> Dict[str, Any]:
    success, response_data = make_api_request("DescribeCodingCurrentUser")
    if not success:
        return response_data

    if not isinstance(response_data, dict):
        return handle_api_error(
            "INVALID_RESPONSE",
            Exception(f"预期为字典，实际为 {type(response_data).__name__}"),
        )

    if "Response" in response_data:
        response = response_data["Response"]
        user_data = response.get("User") or response.get("UserInfo")

        if user_data and _user_info(user_data):
            return user_data

    return handle_api_error(
        "INVALID_USER_DATA", Exception("API响应中未找到有效的用户信息")
    )


def get_user_id() -> int:
    """
    从用户信息中获取 UserId
    :return: 用户ID
    """
    user_info = fetch_coding_user_info()
    if isinstance(user_info, dict) and "Id" in user_info:
        return user_info["Id"]
    raise ValueError("无法获取有效的用户ID")


if __name__ == "__main__":
    user_info = fetch_coding_user_info()
    print("用户信息:", user_info)
    try:
        print("用户ID:", get_user_id())
    except ValueError as e:
        print(f"错误: {e}")
