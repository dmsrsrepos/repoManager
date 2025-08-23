from typing import Dict, Any, List, Optional, Union
import json
import os
from datetime import datetime
from utils import validate_id, handle_api_error
from user_info import make_api_request
from projects_info import get_project_ids


def fetch_repositories_info(
    project_id: Optional[int] = None,
) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    if project_id is not None and not validate_id(project_id, "项目ID"):
        return handle_api_error("INVALID_ID", Exception("项目ID必须为正整数"))

    payload_data = {"ProjectId": project_id} if project_id else {}
    success, response_data = make_api_request("DescribeProjectDepots", payload_data)
    # print(response_data)
    if not success:
        return response_data

    if (
        "Response" in response_data
        and "Data" in response_data["Response"]
        and "DepotList" in response_data["Response"]["Data"]
    ):
        repositories = response_data["Response"]["Data"]["DepotList"]
        return repositories if repositories else []

    return handle_api_error("INVALID_RESPONSE", Exception("API响应中未找到仓库信息"))


def get_all_repos_info(unique: bool = True) -> List[Dict[str, Any]]:
    """
    获取用户所有项目的仓库信息
    :param unique: 是否去除重复的仓库信息，默认为True
    :return: 所有仓库信息列表
    """

    project_ids = get_project_ids()
    print(f"项目ID列表: {project_ids}")
    all_repos = []

    for project_id in project_ids:
        repos = fetch_repositories_info(project_id)
        if isinstance(repos, list):
            all_repos.extend(repos)
        elif isinstance(repos, dict):
            all_repos.append(repos)

    if not unique:
        return all_repos

    seen_ids = set()
    unique_repos = []
    for repo in all_repos:
        if isinstance(repo, dict) and "Id" in repo and repo["Id"] not in seen_ids:
            seen_ids.add(repo["Id"])
            unique_repos.append(repo)

    return unique_repos
