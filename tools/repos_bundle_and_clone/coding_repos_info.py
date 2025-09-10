from typing import Dict, Any, List, Optional, Union
from coding_utils import validate_id, handle_api_error, make_api_request
from coding_projects_info import get_project_ids
from util_filter_repos import filter_repos
from util_repo import save_to_json


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


def get_all_repos_info() -> List[Dict[str, Any]]:
    """
    获取用户所有项目的仓库信息
    :param unique: 是否去除重复的仓库信息，默认为True
    :return: 所有仓库信息列表
    """

    project_ids = get_project_ids()
    print(f"项目ID列表: {project_ids}")
    all_repos = []

    for project_id in project_ids:
        formated_repos = fetch_repositories_info(project_id)
        if isinstance(formated_repos, list):
            all_repos.extend(formated_repos)
        elif isinstance(formated_repos, dict):
            all_repos.append(formated_repos)

    save_to_json(
        org="tencent_org", all_repos=all_repos, prefix="origin_all_coding_repos"
    )

    formated_repos = [
        {"Name": repo["Name"], "Url": repo["DepotHttpsUrl"]}
        for repo in all_repos
        if isinstance(repo, dict)
    ]

    return filter_repos(formated_repos)


if __name__ == "__main__":

    all_repos = get_all_repos_info(False)

    print("仓库数量:", len(all_repos))
    print("所有仓库信息:", all_repos)
