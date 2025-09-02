import requests
import json
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(".env.local"))
load_dotenv()

# filename = f"./github_repos_{org}.json"
def fetch_repositories_info():
    org = os.getenv("ORG_NAME")
    if not org:
        raise ValueError("ORG_NAME environment variable is not set.")

    access_token = os.getenv("WORK_GITHUB_TOKEN")
    if not access_token:
        raise ValueError("WORK_GITHUB_TOKEN environment variable is not set.")
    # print(access_token)
    # 生成带有日期的文件名
   
    repos = []
    page = 1
    per_page = 100  # 每页最大数量

    while True:
        url = f"https://api.github.com/orgs/{org}/repos?type=private&page={page}&per_page={per_page}"
        # print(url)

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

    return repos, org

if __name__ == "__main__":
    repos, org = fetch_repositories_info()