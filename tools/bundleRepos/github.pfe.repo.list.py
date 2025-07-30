"""
GitHub 仓库列表获取工具

该模块用于获取指定GitHub组织下的所有仓库信息，并将其保存为JSON格式文件。
主要功能包括：
- 通过GitHub API获取组织下的仓库列表
- 处理API分页和错误情况
- 将仓库信息保存为JSON文件

环境变量要求：
- ORG_NAME: GitHub组织名称
- WORK_GITHUB_TOKEN: GitHub访问令牌
- BUNDLE_OUTPUT_DIR: 输出目录路径

示例用法：
    设置环境变量后直接运行本脚本
"""

import requests
import json
import os
from datetime import datetime
from bundle_github_repos import main
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()

org = os.getenv("ORG_NAME")
if not org:
    raise ValueError("ORG_NAME environment variable is not set.")

access_token = os.getenv("WORK_GITHUB_TOKEN")
if not access_token:
    raise ValueError("WORK_GITHUB_TOKEN environment variable is not set.")
OUTPUT_DIR = os.getenv("BUNDLE_OUTPUT_DIR")
if not OUTPUT_DIR:
    raise ValueError("BUNDLE_OUTPUT_DIR environment variable is not set.")

# 新增API参数配置
API_TYPE = os.getenv("GITHUB_API_TYPE", "private")
API_PER_PAGE = os.getenv("GITHUB_API_PER_PAGE", "100")
API_TIMEOUT = int(os.getenv("GITHUB_API_TIMEOUT", "30"))
# 生成带有日期的文件名
current_date = datetime.now().strftime("%Y%m%d")
script_dir = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
filename = os.path.normpath(
    os.path.join(script_dir, f"github_repos_{org}_{current_date}.json")
)
# filename = f"./github_repos_{org}.json"

repos = []
page = 1
per_page = 100  # 每页最大数量

session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))

base_url = f"https://api.github.com/orgs/{org}/repos?type={API_TYPE}"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/vnd.github.v3+json",
}

while True:
    url = f"{base_url}&page={page}&per_page={API_PER_PAGE}"
    try:
        response = session.get(url, headers=headers, timeout=API_TIMEOUT)

        # 验证响应状态码
        if response.status_code != 200:
            print(f"Error: API request failed with status code {response.status_code}")
            if response.status_code == 403:
                rate_limit = response.headers.get("X-RateLimit-Remaining", "unknown")
                reset_time = response.headers.get("X-RateLimit-Reset", "unknown")
                print(
                    f"Warning: Approaching GitHub API rate limit. Remaining requests: {rate_limit}, Reset time: {reset_time}"
                )

            print(f"Error details:{response.text}")
            break

        # 验证JSON响应结构
        try:
            current_repos = response.json()
            if not isinstance(current_repos, list):
                print(
                    "Error: Invalid API response format - expected list of repositories"
                )
                break
        except ValueError:
            print("Error: Failed to parse API response as JSON")
            break
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        break

    current_repos = response.json()
    if not current_repos:
        break
    current_repos = [
        {
            "id": repo["id"],
            "name": repo["name"],
            "full_name": repo["full_name"],
            # "private": repo["private"],
            "clone_url": repo["clone_url"],
            # "html_url": repo["html_url"],
            # "updated_at": repo["updated_at"],
        }
        for repo in current_repos
        if repo["clone_url"]
    ]

    repos.extend(current_repos)
    page += 1

print(f"Total private repos: {len(repos)}")
# print(repos)


# 将仓库信息保存到JSON文件
try:
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(repos, f, indent=2, ensure_ascii=False)
    print(f"Successfully saved {len(repos)} repositories to {filename}")
except Exception as e:
    print(f"Error saving to JSON file: {e}")


main(filename, OUTPUT_DIR)
