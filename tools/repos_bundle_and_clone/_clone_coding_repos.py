"""
Coding仓库打包工具

该模块提供了从Coding下载、打包和管理多个代码仓库的功能。
支持从JSON配置文件读取仓库信息，克隆指定仓库，并将它们打包成单一归档文件。
主要用于代码仓库的批量管理、备份和分发。
"""

import os
from util_clone_repos import clone_or_pull_repos
from coding_repos_info import get_all_repos_info
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(".env.local"))
load_dotenv()

if __name__ == "__main__":

    repos = get_all_repos_info()
    org = "codingcorp"
    Repo_Clone_DIR = os.getenv("Repo_OUTPUT_DIR")

    print(f"即将处理 {len(repos)} 个仓库")
    clone_or_pull_repos(repos, Repo_Clone_DIR)
