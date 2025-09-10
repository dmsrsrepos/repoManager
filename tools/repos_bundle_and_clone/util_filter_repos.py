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
    all = len(repos)
    filtered_repos = []
    # print(f"过滤掉的仓库: {IGNORE_REPOS}")
    print(f"忽略的仓库: {IGNORE_REPOS}")


    # print(f"只处理仓库: {ONLY_PROCESS_REPOS}")
    if not ONLY_PROCESS_REPOS or len(ONLY_PROCESS_REPOS) == 0:
        print(f"只处理仓库: All")
        filtered_repos = [repo for repo in repos if repo["Name"] not in IGNORE_REPOS]
    else:
        print(f"只处理仓库: {ONLY_PROCESS_REPOS}")
        filtered_repos = [
            repo
            for repo in repos
            if repo["Name"] in ONLY_PROCESS_REPOS and repo["Name"] not in IGNORE_REPOS
        ]
    filtered = len(filtered_repos)
    print(f"过滤前仓库数量: {all}, 过滤后仓库数量: {filtered}")
    return filtered_repos
