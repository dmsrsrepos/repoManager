from datetime import datetime
import json
import os
from typing import Dict, Any

from repositories_info import get_all_repos_info
from bundle_coding_repos import main

if __name__ == "__main__":
    all_repos = get_all_repos_info(False)
    org = "codingcorp"
    OUTPUT_DIR = os.getenv("BUNDLE_OUTPUT_DIR")

    # 获取仓库信息
    # 生成带有日期的文件名
    current_date = datetime.now().strftime("%Y%m%d")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(script_dir, f"coding_repos_{org}_{current_date}.json")
    # 将仓库信息保存到JSON文件
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(all_repos, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved {len(all_repos)} repositories to {filename}")
    except Exception as e:
        print(f"Error saving to JSON file: {e}")

    main(filename, OUTPUT_DIR)
