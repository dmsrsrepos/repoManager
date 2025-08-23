import json
import os
import subprocess
import sys
import tempfile
import shutil
from datetime import datetime


def read_repos_from_json(json_file):
    """从JSON文件中读取仓库信息"""
    try:
        with open(json_file, "r") as f:
            repos_data = json.load(f)

        # 提取所有仓库的clone_url
        repos = []
        for repo in repos_data:
            if "clone_url" in repo:
                repos.append({"name": repo["name"], "clone_url": repo["clone_url"]})

        return repos
    except Exception as e:
        print(f"读取JSON文件时出错: {e}")
        return []


def bundle_repo(repo_name, clone_url, output_dir):
    """将仓库打包成git bundle，支持增量更新"""
    print(f"正在处理仓库: {repo_name}")

    # 查找现有的bundle文件
    existing_bundles: list[str] = []
    for file in os.listdir(output_dir):
        if file.startswith(f"{repo_name}_") and file.endswith(".bundle"):
            existing_bundles.append(os.path.join(output_dir, file))

    # 按修改时间排序，获取最新的bundle文件
    existing_bundle = None
    if existing_bundles:
        existing_bundles.sort(key=os.path.getmtime, reverse=True)
        existing_bundle = existing_bundles[0]
        print(f"  找到现有bundle文件: {os.path.basename(existing_bundle)}")

        for i, expired_file in enumerate(existing_bundles[1:], 1):
            os.remove(expired_file)
            print(f"    已删除旧bundle文件: {os.path.basename(expired_file)}")
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    try:
        os.chdir(temp_dir)

        if existing_bundle:
            # 如果存在bundle文件，使用它作为基础进行增量更新
            print(f"  正在进行增量更新...")

            # 初始化Git仓库
            subprocess.run(
                ["git", "init"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            # 从bundle文件中获取对象和引用
            subprocess.run(
                ["git", "bundle", "unbundle", existing_bundle],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # 添加远程源
            subprocess.run(
                ["git", "remote", "add", "origin", clone_url],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # 获取所有分支和标签的更新
            fetch_process = subprocess.run(
                ["git", "fetch", "--all", "--tags", "--force"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            if fetch_process.returncode != 0:
                print(f"  获取更新失败: {fetch_process.stderr}")
                return False
        else:
            # 如果不存在bundle文件，直接克隆仓库
            print(f"  正在克隆仓库...")
            clone_process = subprocess.run(
                ["git", "clone", "--mirror", clone_url, "."],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            if clone_process.returncode != 0:
                print(f"  克隆仓库失败: {clone_process.stderr}")
                return False

        # 创建新的bundle文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bundle_filename = f"{repo_name}_{timestamp}.bundle"
        bundle_path = os.path.join(output_dir, bundle_filename)

        # 创建bundle
        print(f"  正在创建bundle...")
        bundle_process = subprocess.run(
            ["git", "bundle", "create", bundle_path, "--all"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if bundle_process.returncode != 0:
            print(f"  创建bundle失败: {bundle_process.stderr}")
            return False

        # 如果成功创建新bundle并且存在旧bundle，可以选择删除旧bundle以节省空间
        # 这里我们保留旧bundle作为历史记录，如果需要删除可以取消下面的注释
        if existing_bundle:
            os.remove(existing_bundle)
            print(f"  已删除旧bundle文件: {os.path.basename(existing_bundle)}")

        print(f"  成功创建bundle: {bundle_path}")
        return True

    except Exception as e:
        print(f"  处理仓库时出错: {e}")
        return False

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)


def main(json_file, output_dir):

    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 读取仓库信息
    repos = read_repos_from_json(json_file)
    if not repos:
        print("没有找到仓库信息")
        sys.exit(1)

    print(f"找到 {len(repos)} 个仓库")
    ignore_repos = ["BACKUP-CHINA"]

    # 过滤掉忽略的仓库
    # 处理每个仓库
    success_count = 1
    for i, repo in enumerate(repos, 1):
        if repo["name"] in ignore_repos:
            print(f"\n[{i}/{len(repos)}][{success_count}] 忽略仓库: {repo['name']}")
        else:
            print(f"\n[{i}/{len(repos)}][{success_count}] 处理仓库: {repo['name']}")
            if bundle_repo(repo["name"], repo["clone_url"], output_dir):
                success_count += 1
            else:
                print(
                    f"\n[{i}/{len(repos)}][{success_count}] 处理失败: {repo['name']}:{repo['clone_url']}"
                )

    print(f"\n完成! 成功处理 {success_count}/{len(repos)} 个仓库")


if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) < 3:
        print("用法: python bundle_github_repos.py <json文件路径> <输出目录>")
        sys.exit(1)

    json_file = sys.argv[1]
    output_dir = sys.argv[2]
    # 调用 main 函数并传递参数
    main(json_file, output_dir)
