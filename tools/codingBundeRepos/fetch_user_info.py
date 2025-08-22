import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
from user_info import fetch_coding_user_info
from projects_info import fetch_projects_info
from repositories_info import fetch_repositories_info

os.makedirs("logs", exist_ok=True)
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            os.path.join("logs", f"coding_api_{datetime.now().strftime('%Y%m%d')}.log")
        ),
    ],
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:

        user_info = fetch_coding_user_info()
        if not user_info or "error" in user_info:
            sys.exit(1)

        user_projects = fetch_projects_info(user_info.get("Id"))
        if not user_projects or (
            isinstance(user_projects, dict) and "error" in user_projects
        ):
            sys.exit(1)

        if user_projects and isinstance(user_projects, list):
            first_project = user_projects[0]
            if first_project:
                fetch_repositories_info(first_project.get("Id"))
    except Exception as e:
        logger.error("程序执行失败: %s", e)
