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
from datetime import datetime


def clone_or_pull_repo(
    repo_name: str, repo_Url: str, repo_clone_dir: str
) -> tuple[bool, str]:
    """克隆或拉取仓库"""
    print(f"正在处理仓库: {repo_name}")
    # 确保目标目录的父目录存在
    os.makedirs(repo_clone_dir, exist_ok=True)
    # 创建目标目录路径
    repo_dir = os.path.join(repo_clone_dir, repo_name)

    # 检查目标目录是否存在
    if os.path.exists(repo_dir):
        print("  仓库已存在，执行 git pull...")
        try:
            os.chdir(repo_dir)
            subprocess.run(
                ["git", "pull", "--all", "--tags", "--force"],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                check=True,
                timeout=900,  # 调整为15分钟超时
            )
            print(f"  成功更新仓库: {repo_name}")
            return True, ""
        except subprocess.CalledProcessError as e:
            error_msg = f"拉取仓库失败:Path:{repo_dir} | Error： {e.stderr if hasattr(e, 'stderr') else str(e)}"
            print(f"  {error_msg}")
            return False, error_msg
        except subprocess.TimeoutExpired:
            error_msg = "拉取仓库超时，已终止操作"
            print(f"  {error_msg}")
            return False, error_msg
    else:
        print("  仓库不存在，执行 git clone...")
        try:
            subprocess.run(
                [
                    "git",
                    "clone",
                    # "--mirror",
                    repo_Url,
                    os.path.normpath(repo_dir),
                    "--depth",
                    "1",
                ],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                check=True,
                timeout=900,  # 调整为15分钟超时
            )
            print(f"  成功克隆仓库: {repo_name}")
            return True, ""
        except subprocess.CalledProcessError as e:
            error_msg = f"克隆仓库失败: {e.stderr if hasattr(e, 'stderr') else str(e)}"
            print(f"  {error_msg}")
            return False, error_msg
        except subprocess.TimeoutExpired:
            error_msg = "克隆仓库超时，已终止操作"
            print(f"  {error_msg}")
            return False, error_msg
        except OSError as e:
            error_msg = f"创建目录失败: {e}"
            print(f"  {error_msg}")
            return False, error_msg


def clone_or_pull_repos(repos: list[dict[str, str]], output_dir: str) -> None:

    # 确保输出目录存在
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    except OSError as e:
        print(f"无法创建输出目录 {output_dir}: {e}")
        sys.exit(1)

    if not repos:
        print("没有找到仓库信息")
        sys.exit(1)

    print(f"找到 {len(repos)} 个仓库")
    # 从环境变量或配置文件读取忽略仓库列表
    ignore_repos = (
        os.getenv("IGNORE_REPOS", "").split(",")
        if os.getenv("IGNORE_REPOS")
        else ["BACKUP-CHINA"]
    )

    erRepos = []
    # 处理每个仓库
    success_count = 0
    for i, repo in enumerate(repos, 1):
        if repo["Name"] in ignore_repos:
            print(f"\n[{i}/{len(repos)}] 忽略仓库: {repo['Name']}")
        else:
            print(f"\n[{i}/{len(repos)}] 处理仓库: {repo['Name']}")
            success, error_msg = clone_or_pull_repo(
                repo["Name"], repo["Url"], output_dir
            )
            if success:
                success_count += 1
                print(f"处理成功: {repo['Name']} - 当前成功数: {success_count}/{i}")
            else:
                print(f"处理失败: {repo['Name']} - {repo['Url']}")
                repo["Error"] = error_msg
                erRepos.append(repo)

    current_date = datetime.now().strftime("%Y%m%d")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(script_dir, f"clone_repos_error_{current_date}.log")
    # 将仓库信息保存到JSON文件
    try:
        with open(filename, mode="a", encoding="utf-8") as f:
            json.dump(erRepos, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving to log file: {e}")
    print(f"\n完成! 成功处理 {success_count}/{len(repos)} 个仓库")
