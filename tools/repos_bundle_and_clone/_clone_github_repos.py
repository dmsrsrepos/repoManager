import os
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv(".env.local"))
load_dotenv()

if __name__ == "__main__":
    from github_repo_list import fetch_repositories_info
    from util_clone_repos import clone_or_pull_repos
    repos, org = fetch_repositories_info()
    # 检查命令行参数
    # 将仓库信息保存到JSON文件
    Repo_Clone_DIR = os.getenv("Repo_OUTPUT_DIR")

    if not Repo_Clone_DIR:
        raise ValueError("Repo_OUTPUT_DIR environment variable is not set.")

    print(f"即将处理 {len(repos)} 个仓库")
    clone_or_pull_repos(repos, Repo_Clone_DIR)
