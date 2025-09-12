import os
from typing import Any, Dict, List


IGNORE_REPOS = (
    os.getenv("IGNORE_REPOS", "").split(",")
    if os.getenv("IGNORE_REPOS")
    else ["BACKUP-CHINA"]
)
ONLY_PROCESS_REPOS = (
    os.getenv("ONLY_PROCESS_REPOS", "").split(",")
    if os.getenv("ONLY_PROCESS_REPOS")
    else []
)


def filter_repos(repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    all_repos = len(repos)
    filtered_repos = []

    # print(f"只处理仓库: {ONLY_PROCESS_REPOS}")
    if not ONLY_PROCESS_REPOS or len(ONLY_PROCESS_REPOS) == 0:
        print(f"处理全部仓库，但忽略仓库: {IGNORE_REPOS}")
        filtered_repos = [repo for repo in repos if repo["Name"] not in IGNORE_REPOS]
    else:
        print(f"只处理仓库: {ONLY_PROCESS_REPOS}，而且忽略其中的仓库: {IGNORE_REPOS}")
        filtered_repos = [
            repo
            for repo in repos
            if repo["Name"] in ONLY_PROCESS_REPOS and repo["Name"] not in IGNORE_REPOS
        ]
    filtered = len(filtered_repos)
    print(f"过滤前仓库数量: {all_repos}, 过滤后仓库数量: {filtered}")
    return filtered_repos
