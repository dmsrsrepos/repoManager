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
from concurrent.futures import ProcessPoolExecutor, as_completed


def read_repos_from_json(json_file_path):
    """从JSON文件中读取仓库信息"""
    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            repos_data = json.load(f)

        # 验证JSON数据格式
        if not isinstance(repos_data, list):
            print("错误: JSON文件格式不正确，应为列表格式")
            return []

        # 提取所有仓库的clone_url
        repos = []
        for repo in repos_data:
            if not isinstance(repo, dict):
                print("警告: 跳过非字典格式的仓库数据")
                continue
            if "DepotSshUrl" in repo and "Name" in repo:
                if isinstance(repo["Name"], str) and isinstance(
                    repo["DepotSshUrl"], str
                ):
                    repos.append(
                        {
                            "Name": repo["Name"],
                            "DepotSshUrl": repo["DepotSshUrl"],
                            "DepotHttpsUrl": repo.get("DepotHttpsUrl", ""),
                        }
                    )
                else:
                    print(f"警告: 仓库数据字段类型不正确: {repo}")
            else:
                print(f"警告: 仓库数据缺少必要字段: {repo}")

        return repos
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return []
    except FileNotFoundError:
        print(f"错误: 文件未找到: {json_file_path}")
        return []
    except OSError as e:
        print(f"读取JSON文件时出错: {e}")
        return []


def clone_or_pull_repo(repo_name, DepotSshUrl, repo_clone_dir):
    """克隆或拉取仓库"""
    print(f"正在处理仓库: {repo_name}")
    # 确保目标目录的父目录存在
    os.makedirs(os.path.dirname(repo_clone_dir), exist_ok=True)
    # 创建目标目录路径
    repo_dir = os.path.join(repo_clone_dir, repo_name)

    # 检查目标目录是否存在
    if os.path.exists(repo_dir):
        print("  仓库已存在，执行 git pull...")
        try:
            os.chdir(repo_dir)
            pull_process = subprocess.run(
                ["git", "pull", "--all", "--tags", "--force"],
                text=True,
                capture_output=True,
                check=True,
                timeout=900,  # 调整为15分钟超时
            )
            print(f"  成功更新仓库: {repo_name}")
            return True, ""
        except subprocess.CalledProcessError as e:
            error_msg = f"拉取仓库失败: {e.stderr if hasattr(e, 'stderr') else str(e)}"
            print(f"  {error_msg}")
            return False, error_msg
        except subprocess.TimeoutExpired:
            error_msg = "拉取仓库超时，已终止操作"
            print(f"  {error_msg}")
            return False, error_msg
    else:
        print("  仓库不存在，执行 git clone...")
        try:
            import shlex

            clone_process = subprocess.run(
                [
                    "git",
                    "clone",
                    # "--mirror",
                    DepotSshUrl,
                    os.path.normpath(repo_dir),
                ],
                text=True,
                capture_output=True,
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


def main(json_file, output_dir):

    # 确保输出目录存在
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    except OSError as e:
        print(f"无法创建输出目录 {output_dir}: {e}")
        sys.exit(1)

    # 读取仓库信息
    repos = read_repos_from_json(json_file)
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
            if clone_or_pull_repo(repo["Name"], repo["DepotSshUrl"], output_dir):
                success_count += 1
                print(f"处理成功: {repo['Name']} - 当前成功数: {success_count}")
            else:
                print(f"处理失败: {repo['Name']} - {repo['DepotSshUrl']}")
                erRepos.append(repo)

    current_date = datetime.now().strftime("%Y%m%d")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(script_dir, f"coding_repos_error_{current_date}.log")
    # 将仓库信息保存到JSON文件
    try:
        with open(filename, mode="a", encoding="utf-8") as f:
            json.dump(erRepos, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving to log file: {e}")
    print(f"\n完成! 成功处理 {success_count}/{len(repos)} 个仓库")


if __name__ == "__main__":
    from repositories_info import get_all_repos_info

    all_repos = get_all_repos_info(False)
    org = "codingcorp"
    OUTPUT_DIR = os.getenv("Repo_OUTPUT_DIR")

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
