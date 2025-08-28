from typing import Dict, Any, List, Optional, Union
from coding_utils import (
    validate_id,
    handle_api_error,
    make_api_request,
)
from coding_user_info import get_user_id


def fetch_projects_info(
    user_id: Optional[int] = None,
) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    if user_id is not None and not validate_id(user_id, "用户ID"):
        return handle_api_error("INVALID_ID", Exception("用户ID必须为正整数"))

    payload_data = {"UserId": user_id} if user_id else {}
    success, response_data = make_api_request("DescribeUserProjects", payload_data)

    if not success:
        return response_data

    if "Response" in response_data:
        projects = response_data["Response"].get("Projects") or response_data[
            "Response"
        ].get("ProjectList")
        return projects if projects else []

    return handle_api_error("INVALID_RESPONSE", Exception("API响应中未找到项目信息"))


def get_project_ids() -> List[int]:
    """
    获取用户所有项目的ID列表
    :param user_id: 用户ID，可选
    :return: 项目ID列表
    """

    user_id = get_user_id()
    projects = fetch_projects_info(user_id)
    if isinstance(projects, dict):
        projects = [projects]
    return [p["Id"] for p in projects if isinstance(p, dict) and "Id" in p]


if __name__ == "__main__":
    # 测试用例：调用 get_project_ids 并打印结果

    print("测试 get_project_ids 函数:")
    project_ids = get_project_ids()
    print(f"项目ID列表: {project_ids}")
