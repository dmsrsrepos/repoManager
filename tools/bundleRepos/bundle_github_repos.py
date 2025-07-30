"""
GitHub仓库打包工具

该模块提供了从GitHub下载、打包和管理多个代码仓库的功能。
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
            if "clone_url" in repo and "name" in repo:
                if isinstance(repo["name"], str) and isinstance(repo["clone_url"], str):
                    repos.append({"name": repo["name"], "clone_url": repo["clone_url"]})
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


def bundle_repo(repo_name, clone_url, output_dir_path):
    """将仓库打包成git bundle，支持增量更新"""
    print(f"正在处理仓库: {repo_name}")

    # 查找现有的bundle文件
    existing_bundles: list[str] = []
    for file in os.listdir(output_dir_path):
        if file.startswith(f"{repo_name}_") and file.endswith(".bundle"):
            existing_bundles.append(os.path.join(output_dir_path, file))

    # 按修改时间排序，获取最新的bundle文件
    existing_bundle = None
    if existing_bundles:
        existing_bundles.sort(key=os.path.getmtime, reverse=True)
        existing_bundle = existing_bundles[0]
        print(f"  找到现有bundle文件: {os.path.basename(existing_bundle)}")

        for i, expired_file in enumerate(existing_bundles[1:], 1):
            os.remove(expired_file)
            print(
                f"    已删除旧bundle文件: {os.path.basename(expired_file)},"
                f"序号：{i}/{len(existing_bundles)-1}"
            )
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    try:
        os.chdir(temp_dir)

        if existing_bundle:
            # 如果存在bundle文件，使用它作为基础进行增量更新
            print("  正在进行增量更新...")

            # 合并初始化、解包和添加远程操作
            try:
                subprocess.run(
                    ["git", "init"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                    timeout=300,  # 添加5分钟超时
                )
            except subprocess.CalledProcessError as e:
                print(
                    f"  git初始化失败: {e.stderr if hasattr(e, 'stderr') else str(e)}"
                )
                return False
            except subprocess.TimeoutExpired:
                print(f"  git初始化超时，已终止操作")
                return False

            # 分步执行命令并添加错误处理
            try:
                subprocess.run(
                    ["git", "bundle", "unbundle", existing_bundle],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=600,  # 添加10分钟超时
                )
            except subprocess.CalledProcessError as e:
                print(
                    f"  解包bundle文件失败: {e.stderr if hasattr(e, 'stderr') else str(e)}"
                )
                return False
            except subprocess.TimeoutExpired:
                print(f"  解包bundle文件超时，已终止操作")
                return False

            try:
                subprocess.run(
                    ["git", "remote", "add", "origin", clone_url],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=300,  # 添加5分钟超时
                )
            except subprocess.CalledProcessError as e:
                print(
                    f"  添加远程仓库失败: {e.stderr if hasattr(e, 'stderr') else str(e)}"
                )
                return False
            except subprocess.TimeoutExpired:
                print(f"  添加远程仓库超时，已终止操作")
                return False

            # 获取所有分支和标签的更新
            try:
                fetch_process = subprocess.run(
                    ["git", "fetch", "--all", "--tags", "--force"],
                    text=True,
                    capture_output=True,
                    check=True,
                    timeout=1800,  # 添加30分钟超时
                )
                # 如果执行到这里，说明命令成功执行（因为check=True会在失败时抛出异常）
            except subprocess.CalledProcessError as e:
                print(f"  获取更新失败: {e.stderr if hasattr(e, 'stderr') else str(e)}")
                return False
            except subprocess.TimeoutExpired:
                print(f"  获取更新超时，已终止操作")
                return False
        else:
            # 如果不存在bundle文件，直接克隆仓库
            print("  正在克隆仓库...")
            try:
                clone_process = subprocess.run(
                    ["git", "clone", "--mirror", clone_url, "."],
                    text=True,
                    capture_output=True,
                    check=True,
                    timeout=1800,  # 添加30分钟超时
                )
                # 如果执行到这里，说明命令成功执行
            except subprocess.CalledProcessError as e:
                print(f"  克隆仓库失败: {e.stderr if hasattr(e, 'stderr') else str(e)}")
                return False
            except subprocess.TimeoutExpired:
                print(f"  克隆仓库超时，已终止操作")
                return False

        # 创建新的bundle文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bundle_filename = f"{repo_name}_{timestamp}.bundle"
        bundle_path = os.path.join(output_dir_path, bundle_filename)

        # 创建bundle
        print("  正在创建bundle...")
        # 创建包含所有引用的git bundle文件
        try:
            bundle_process = subprocess.run(
                ["git", "bundle", "create", bundle_path, "--all"],
                capture_output=True,
                text=True,
                check=True,
                timeout=1800,  # 添加30分钟超时
            )
            print(f"  成功创建bundle: {bundle_path}")
        except subprocess.CalledProcessError as e:
            print(f"  创建bundle失败: {e.stderr if hasattr(e, 'stderr') else str(e)}")
            return False
        except subprocess.TimeoutExpired:
            print(f"  创建bundle超时，已终止操作")
            return False

        # 只有在成功创建新bundle后才删除旧bundle
        if existing_bundle:
            try:
                os.remove(existing_bundle)
                print(f"  已删除旧bundle文件: {os.path.basename(existing_bundle)}")
            except OSError as e:
                print(f"  删除旧bundle文件失败: {e}")

        return True

    except Exception as e:
        print(f"  处理仓库时出错: {e}")
        return False

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)


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

    # 处理每个仓库
    success_count = 0
    for i, repo in enumerate(repos, 1):
        if repo["name"] in ignore_repos:
            print(f"\n[{i}/{len(repos)}] 忽略仓库: {repo['name']}")
        else:
            print(f"\n[{i}/{len(repos)}] 处理仓库: {repo['name']}")
            if bundle_repo(repo["name"], repo["clone_url"], output_dir):
                success_count += 1
                print(f"处理成功: {repo['name']} - 当前成功数: {success_count}")
            else:
                print(f"处理失败: {repo['name']} - {repo['clone_url']}")

    print(f"\n完成! 成功处理 {success_count}/{len(repos)} 个仓库")


if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) < 3:
        print("用法: python bundle_github_repos.py <json文件路径> <输出目录>")
        sys.exit(1)

    json_file = os.path.abspath(sys.argv[1])
    output_dir = os.path.abspath(sys.argv[2])

    # 验证输入参数
    if not os.path.isfile(json_file):
        print(f"错误: JSON文件不存在: {json_file}")
        sys.exit(1)

    # 确保输出目录的父目录存在
    output_parent_dir = os.path.dirname(output_dir)
    if output_parent_dir and not os.path.exists(output_parent_dir):
        try:
            os.makedirs(output_parent_dir)
            print(f"已创建输出目录的父目录: {output_parent_dir}")
        except OSError as e:
            print(f"错误: 无法创建输出目录的父目录: {output_parent_dir}, 错误: {e}")
            sys.exit(1)
    # 调用 main 函数并传递参数
    main(json_file, output_dir)
