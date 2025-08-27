"""
Coding仓库打包工具

该模块提供了从Coding下载、打包和管理多个代码仓库的功能。
支持从JSON配置文件读取仓库信息，克隆指定仓库，并将它们打包成单一归档文件。
主要用于代码仓库的批量管理、备份和分发。
"""

import json
import os
import subprocess
import sys
import tempfile
import shutil
from datetime import datetime
from py_utils import bundle_repos, read_repos_from_json


if __name__ == "__main__":
    from repositories_info import get_all_repos_info

    all_repos = get_all_repos_info(False)
    org = "codingcorp"
    OUTPUT_DIR = os.getenv("BUNDLE_OUTPUT_DIR")

    # 获取仓库信息
    # 生成带有日期的文件名
    current_date = datetime.now().strftime("%Y%m%d")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(script_dir, f"coding_repos_{org}_{current_date}.json")
    # 将仓库信息保存到JSON文件
    try:
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(all_repos, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved {len(all_repos)} repositories to {json_file}")
    except Exception as e:
        print(f"Error saving to JSON file: {e}")

    repos = [
        {"Name": repo["name"], "Url": repo["DepotHttpsUrl"]}
        for repo in all_repos
        if isinstance(repo, dict)
    ]

    bundle_repos(repos, OUTPUT_DIR)
