import requests
import json
import os
from datetime import datetime
from bundle_github_repos import main
from dotenv import load_dotenv

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
# 生成带有日期的文件名
current_date = datetime.now().strftime("%Y%m%d")
script_dir = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(script_dir, f"github_repos_{org}_{current_date}.json")
# filename = f"./github_repos_{org}.json"

repos = []
page = 1
per_page = 100  # 每页最大数量

while True:
    url = f"https://api.github.com/orgs/{org}/repos?type=private&page={page}&per_page={per_page}"
    response = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
        },
    )

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
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
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(repos, f, indent=2, ensure_ascii=False)
    print(f"Successfully saved {len(repos)} repositories to {filename}")
except Exception as e:
    print(f"Error saving to JSON file: {e}")


# main(filename, OUTPUT_DIR)
