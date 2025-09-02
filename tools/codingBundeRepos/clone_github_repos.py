from datetime import datetime
import json
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(".env.local"))
load_dotenv()

if __name__ == "__main__":
    from github_repo_list import fetch_repositories_info
    from repos_utils.clone_repos import clone_or_pull_repos
    all_repos, org = fetch_repositories_info()
    # 检查命令行参数
    # 将仓库信息保存到JSON文件
    Repo_Clone_DIR = os.getenv("Repo_OUTPUT_DIR")
    if not Repo_Clone_DIR:
        raise ValueError("Repo_OUTPUT_DIR environment variable is not set.")
    current_date = datetime.now().strftime("%Y%m%d")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(script_dir, f"github_repos_{org}_{current_date}.json")
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(all_repos, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved {len(all_repos)} repositories to {filename}")
    except Exception as e:
        print(f"Error saving to JSON file: {e}")

    repos = [
        {"Name": repo["name"], "Url": repo["clone_url"]}
        for repo in all_repos
        if isinstance(repo, dict)
    ]
    print(f"即将处理 {len(repos)} 个仓库")
    clone_or_pull_repos(repos, Repo_Clone_DIR)
