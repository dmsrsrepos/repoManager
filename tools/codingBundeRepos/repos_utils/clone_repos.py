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


def run_command(command: list[str], timeout: int = 900) -> tuple[bool, str]:
    """
    执行命令并统一处理错误
    :param command: 命令列表
    :param timeout: 超时时间（秒）
    :return: (是否成功, 错误信息, 标准输出, 标准错误)
    """
    try:
        result = subprocess.run(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            timeout=timeout,
            close_fds=True,
            shell=False,
        )
        if result.stdout == None:
            return True, ""
        else:
            return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_msg = f"命令执行失败: {e.stderr if e.stderr else str(e)}"
        return False, error_msg
    except subprocess.TimeoutExpired:
        error_msg = "命令执行超时，已终止操作"
        return False, error_msg
    except Exception as e:
        error_msg = f"未知错误: {str(e)}"
        return False, error_msg


def is_shallow_repository(repo_dir: str) -> bool:
    """
    检查仓库是否为浅克隆（shallow repository）
    :param repo_dir: 仓库目录路径
    :return: 是否为浅克隆
    """
    try:
        success, output = run_command(
            ["git", "rev-parse", "--is-shallow-repository"], cwd=repo_dir
        )
        return success and output.strip() == "true"
    except Exception:
        return False


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
            is_shallow = is_shallow_repository(repo_dir)
            pull_command = ["git", "pull", "--all", "--tags", "--force"]
            if is_shallow:
                pull_command.append("--unshallow")

            success, error_msg = run_command(pull_command, 900)
            if success:
                print(f"  成功更新仓库: {repo_name}")
                return True, ""
            else:
                error_msg = f"拉取仓库失败:Path:{repo_dir} | Error： {error_msg}"
                print(f"  {error_msg}")
                return False, error_msg
        except Exception as e:
            error_msg = f"拉取仓库失败: {str(e)}"
            print(f"  {error_msg}")
            return False, error_msg
    else:
        print("  仓库不存在，执行 git clone...")
        success, error_msg = run_command(
            [
                "git",
                "clone",
                repo_Url,
                os.path.normpath(repo_dir),
                "--depth",
                "1",
            ],
            900,
        )
        if success:
            print(f"  成功克隆仓库: {repo_name}")
            return True, ""
        else:
            error_msg = f"克隆仓库失败: {error_msg}"
            print(f"  {error_msg}")
            return False, error_msg


def clone_or_pull_repos(repos: list[dict[str, str]], output_dir: str) -> None:
    """批量克隆或拉取仓库"""
    # 确保输出目录存在
    try:
        os.makedirs(output_dir, exist_ok=True)
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
