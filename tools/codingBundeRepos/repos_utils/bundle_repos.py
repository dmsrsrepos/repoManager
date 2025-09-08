import json
import os
import subprocess
import sys
import tempfile
import shutil
from datetime import datetime


def bundle_repo(repo_name: str, repo_Url: str, output_dir: str) -> tuple[bool, str]:
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
            # os.remove(expired_file)
            os.unlink(expired_file)  # 直接永久删除
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
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    check=True,
                    timeout=60,  # 调整为1分钟超时
                )
            except subprocess.CalledProcessError as e:
                error_msg = (
                    f"git初始化失败: {e.stderr if hasattr(e, 'stderr') else str(e)}"
                )
                print(f"  {error_msg}")
                return False, error_msg
            except subprocess.TimeoutExpired:
                error_msg = "git初始化超时，已终止操作"
                print(f"  {error_msg}")
                return False, error_msg

            # 分步执行命令并添加错误处理
            try:
                subprocess.run(
                    ["git", "bundle", "unbundle", existing_bundle],
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    text=True,
                    check=True,
                    timeout=300,  # 调整为5分钟超时
                )
            except subprocess.CalledProcessError as e:
                error_msg = f"解包bundle文件失败: {e.stderr if hasattr(e, 'stderr') else str(e)}"
                print(f"  {error_msg}")
                return False, error_msg
            except subprocess.TimeoutExpired:
                error_msg = "解包bundle文件超时，已终止操作"
                print(f"  {error_msg}")
                return False, error_msg

            try:
                subprocess.run(
                    ["git", "remote", "add", "origin", repo_Url],
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    text=True,
                    check=True,
                    timeout=60,  # 调整为1分钟超时
                )
            except subprocess.CalledProcessError as e:
                error_msg = (
                    f"添加远程仓库失败: {e.stderr if hasattr(e, 'stderr') else str(e)}"
                )
                print(f"  {error_msg}")
                return False, error_msg
            except subprocess.TimeoutExpired:
                error_msg = "添加远程仓库超时，已终止操作"
                print(f"  {error_msg}")
                return False, error_msg

            # 获取所有分支和标签的更新
            try:
                fetch_process = subprocess.run(
                    [
                        "git",
                        "fetch",
                        "--all",
                        "--tags",
                        "--force",
                        #  "--depth", "1"
                    ],
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    text=True,
                    check=True,
                    timeout=900,  # 调整为15分钟超时
                )
                # 如果执行到这里，说明命令成功执行（因为check=True会在失败时抛出异常）
            except subprocess.CalledProcessError as e:
                error_msg = (
                    f"获取更新失败: {e.stderr if hasattr(e, 'stderr') else str(e)}"
                )
                print(f"  {error_msg}")
                return False, error_msg
            except subprocess.TimeoutExpired:
                error_msg = "获取更新超时，已终止操作"
                print(f"  {error_msg}")
                return False, error_msg
        else:
            # 如果不存在bundle文件，直接克隆仓库
            print("  正在克隆仓库...")
            try:
                clone_process = subprocess.run(
                    [
                        "git",
                        "clone",
                        # "--mirror",
                        repo_Url,
                        ".",
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
                # 如果执行到这里，说明命令成功执行
            except subprocess.CalledProcessError as e:
                error_msg = (
                    f"克隆仓库失败: {e.stderr if hasattr(e, 'stderr') else str(e)}"
                )
                print(f"  {error_msg}")
                return False, error_msg
            except subprocess.TimeoutExpired:
                error_msg = "克隆仓库超时，已终止操作"
                print(f"  {error_msg}")
                return False, error_msg

        # 创建新的bundle文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bundle_filename = f"{repo_name}_{timestamp}.bundle"
        bundle_path = os.path.join(output_dir, bundle_filename)

        # 创建bundle
        print("  正在创建bundle...")
        # 创建包含所有引用的git bundle文件
        try:
            subprocess.run(
                ["git", "bundle", "create", bundle_path, "--all"],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                check=True,
                timeout=900,  # 调整为15分钟超时
            )
            print(f"  成功创建bundle: {bundle_path}")
        except subprocess.CalledProcessError as e:
            error_msg = (
                f"创建bundle失败: {e.stderr if hasattr(e, 'stderr') else str(e)}"
            )
            print(f"  {error_msg}")
            return False, error_msg
        except subprocess.TimeoutExpired:
            error_msg = "创建bundle超时，已终止操作"
            print(f"  {error_msg}")
            return False, error_msg

        # 只有在成功创建新bundle后才删除旧bundle
        if existing_bundle:
            try:
                # os.remove(existing_bundle)
                os.unlink(existing_bundle)  # 直接永久删除
                # shutil.rmtree(existing_bundle)  # 直接永久删除目录
                print(f"  已删除旧bundle文件: {os.path.basename(existing_bundle)}")
            except OSError as e:
                print(f"  删除旧bundle文件失败: {e}")

        print(f"  成功创建bundle: {bundle_path}")
        return True, ""

    except Exception as e:
        error_msg = f"处理仓库时出错: {e}"
        print(f"  {error_msg}")
        return False, error_msg

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)


def bundle_repos(repos: list[dict[str, str]], output_dir: str) -> None:

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
            success, error_msg = bundle_repo(repo["Name"], repo["Url"], output_dir)
            if success:
                success_count += 1
                print(f"处理成功: {repo['Name']} - 当前成功数: {success_count}/{i}")
            else:
                print(f"处理失败: {repo['Name']} - {repo['Url']}")
                repo["Error"] = error_msg
                erRepos.append(repo)

    current_date = datetime.now().strftime("%Y%m%d")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(script_dir, f"bundle_repos_error_{current_date}.log")
    # 将仓库信息保存到JSON文件
    try:
        with open(filename, mode="a", encoding="utf-8") as f:
            json.dump(erRepos, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving to log file: {e}")
    print(f"\n完成! 成功处理 {success_count}/{len(repos)} 个仓库")
