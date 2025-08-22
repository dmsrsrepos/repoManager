import requests
import json
import os
from datetime import datetime
from bundle_github_repos import main
from dotenv import load_dotenv

load_dotenv()

org = os.getenv("ORG_NAME")
access_token = os.getenv("WORK_GITHUB_TOKEN")
OUTPUT_DIR = os.getenv("BUNDLE_OUTPUT_DIR")
# 生成带有日期的文件名
current_date = datetime.now().strftime("%Y%m%d")
filename = f"github_repos_{org}_{current_date}.json"
# filename = f"github_repos_{org}.json"
print(org, access_token, OUTPUT_DIR)
