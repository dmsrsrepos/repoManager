import json
import os
import stat
import subprocess
import sys
import tempfile
import shutil
import time
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
            # stdin，stdout，stderr 不指定参数时将会显示命令执行的过程，比如clone的进度等
            # stdin=subprocess.PIPE,
            # stdout=subprocess.PIPE,
            # stderr=subprocess.PIPE,
            text=True,
            check=True,
            timeout=timeout,
            close_fds=True,
            shell=False,
        )
        # if result.stdout == None:
        #     return True, ""
        # else:
        #     return True, result.stdout.strip()
        return True, {result.stdout.strip() if result.stdout else ""}
    except subprocess.CalledProcessError as e:
        error_msg = f"命令执行失败: {e.stderr if e.stderr else str(e)}"
        return False, error_msg
    except subprocess.TimeoutExpired:
        error_msg = "命令执行超时，已终止操作"
        return False, error_msg
    except Exception as e:
        error_msg = f"未知错误: {str(e)}"
        return False, error_msg


def bundle_repo(
    repo_name: str, repo_Url: str, output_dir: str, aways_bundle_new: bool = False
) -> tuple[bool, str]:
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
        if aways_bundle_new:
            print(
                f"  总是创建新的bundle,将在创建成功后删除已找到的bundle文件: {os.path.basename(existing_bundle)}"
            )
        else:
            print(f"  找到现有bundle文件: {os.path.basename(existing_bundle)}")

        for i, expired_file in enumerate(existing_bundles[1:], 1):
            # os.remove(expired_file)
            os.unlink(expired_file)  # 直接永久删除
            print(
                f"    已删除旧bundle文件: {os.path.basename(expired_file)},"
                f"序号：{i}/{len(existing_bundles)-1}"
            )

    temp_root_dir = os.path.join(tempfile.gettempdir(), "repositoryMananger")
    # 确保临时目录存在
    os.makedirs(temp_root_dir, exist_ok=True)

    # 创建临时目录
    temp_dir = mkdtemp_chdir(repo_name, temp_root_dir)
    # print(f"  创建临时目录: {temp_dir}")
    try:

        def _try_clone_repo_from_bundle():
            # 分步执行命令并添加错误处理
            print(f"  开始clone bundle... {existing_bundle}")
            success, error_msg = run_command(
                ["git", "clone", existing_bundle, temp_dir], 300
            )
            if not success:
                print(f"  {error_msg}")
                return False, error_msg
            # print("  clone更新成功")
            # 检查远程仓库是否存在，不存在则添加，存在则更新
            success, error_msg = run_command(["git", "remote", "get-url", "origin"], 60)
            # print(f"  检查远程仓库...{repo_Url}")
            if success:
                # 远程仓库已存在，更新 URL
                success, error_msg = run_command(
                    ["git", "remote", "set-url", "origin", repo_Url], 60
                )
                # print("  远程仓库已存在，更新 URL 成功")
            else:
                # 远程仓库不存在，添加
                success, error_msg = run_command(
                    ["git", "remote", "add", "origin", repo_Url], 60
                )

                # print("  远程仓库不存在，添加成功")
            if not success:
                print(f"  {error_msg}")
                return False, error_msg
            # print("  远程仓库已设置")

            success, error_msg = _fetch_repository(repo_Url, temp_dir)
            if not success:
                return False, error_msg
            # print("  远程仓库已更新")
            return True, ""

        need_to_clone_from_repo_url = None

        if aways_bundle_new:
            print("  设置为总是创建新的bundle,将删除已找到的bundle文件")
            need_to_clone_from_repo_url = True
        elif existing_bundle:
            print("  找到现有bundle文件，将尝试增量更新...")
            success, error_msg = _try_clone_repo_from_bundle()
            if success:
                print("  增量更新 bundle 成功...")
                need_to_clone_from_repo_url = False
            else:
                print(f"  增量更新失败，将尝试重新克隆仓库: {error_msg}")
                need_to_clone_from_repo_url = True
        else:
            print("  未找到现有bundle文件，将尝试克隆仓库...")
            need_to_clone_from_repo_url = True
        if need_to_clone_from_repo_url:
            temp_dir = mkdtemp_chdir(repo_name, temp_root_dir)
            # 如果不存在bundle文件，直接克隆仓库
            print(f"  正在浅克隆仓库...{repo_Url}")
            success, error_msg = run_command(
                [
                    "git",
                    "clone",
                    repo_Url,
                    temp_dir,
                    # ".",
                    #
                    "--depth",
                    "1",
                ],
                900,
            )
            if not success:
                print(f"  {error_msg}")
                return False, error_msg

            success, error_msg = _fetch_repository(repo_Url, temp_dir)
            if not success:
                print(f"  {error_msg}")
                return False, error_msg
        # 创建新的bundle文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bundle_filename = f"{repo_name}_{timestamp}.bundle"
        bundle_path = os.path.join(output_dir, bundle_filename)

        # 创建bundle
        print("  正在创建bundle...")
        success, error_msg = run_command(
            ["git", "bundle", "create", bundle_path, "--all"], 900
        )
        if not success:
            print(f"  {error_msg}")
            return False, error_msg

        # 只有在成功创建新bundle后才删除旧bundle
        if existing_bundle:
            try:
                os.unlink(existing_bundle)  # 直接永久删除
                print(f"  已删除旧bundle文件: {os.path.basename(existing_bundle)}")
            except OSError as e:
                print(f"  删除旧bundle文件失败: {e}")

        print(f"  成功创建bundle: {bundle_path}")
        return True, ""

    except Exception as e:
        error_msg = f"处理仓库时出错: {str(e)}"
        print(f"  {error_msg}")
        return False, error_msg

    finally:
        cleanup_temp_dir(temp_root_dir)

def mkdtemp_chdir(repo_name, temp_root_dir):
    """创建临时目录，并切换到该目录"""
    temp_dir = tempfile.mkdtemp(
            prefix=os.path.normpath(f"tempRepo_{repo_name}_"),
            suffix="_gitRepo",
            dir=temp_root_dir,
            )
    os.chdir(temp_dir)
    return temp_dir


def remove_readonly(func, path, _):
    """清除只读属性并重试删除操作"""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def cleanup_temp_dir(target_dir: str) -> None:
    for root, dirs, files in os.walk(target_dir):
        # for file in files:
        #     file_path = os.path.join(root, file)
        #     try:
        #         os.chmod(file_path, stat.S_IWRITE)  # 修改文件权限
        #         os.unlink(file_path)
        #         # print(f"已删除文件: {file_path}")
        #     except OSError as e:
        #         # print(f"删除文件失败: {file_path}, 错误: {str(e)}")
        #         pass
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            try:
                shutil.rmtree(dir_path, onerror=remove_readonly)  # 处理只读文件
            except OSError as e:
                # print(f"删除目录失败: {dir_path}, 错误: {str(e)}")
                pass


def bundle_repos(
    repos: list[dict[str, str]], output_dir: str, aways_bundle_new: bool = False
) -> None:

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
            success, error_msg = bundle_repo(
                repo["Name"], repo["Url"], output_dir, aways_bundle_new
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
    filename = os.path.join(script_dir, f"bundle_repos_error_{current_date}.log")
    # 将仓库信息保存到JSON文件
    try:
        with open(filename, mode="a", encoding="utf-8") as f:
            json.dump(erRepos, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving to log file: {e}")
    print(f"\n完成! 成功处理 {success_count}/{len(repos)} 个仓库")


def run_command_return_std(command: list[str], timeout: int = 900) -> tuple[bool, str]:
    """
    执行命令并统一处理错误
    :param command: 命令列表
    :param timeout: 超时时间（秒）
    :return: (是否成功, 错误信息, 标准输出, 标准错误)
    """
    try:
        result = subprocess.run(
            command,
            # 需要确保指定stdout=subprocess.PIPE，result.stdout才会有输出值
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            timeout=timeout,
            close_fds=True,
            shell=False,
        )
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
        success, output = run_command_return_std(
            ["git", "rev-parse", "--is-shallow-repository"], timeout=60
        )
        # print(f"  是否为浅克隆: {output}")
        return success and output.strip() == "true"
    except Exception as e:
        print(f"  检查是否为浅克隆时出错: {str(e)}")
        return False


def _fetch_repository(repo_Url: str, temp_dir: str) -> tuple[bool, str]:
    """执行 git fetch 操作"""
    os.chdir(temp_dir)
    shallow_fetch = is_shallow_repository(temp_dir)
    command = [
        "git",
        "fetch",
        "--all",
        "--tags",
        "--prune",
    ]
    if shallow_fetch:
        print("  此仓库为浅克隆，将执行 --unshallow 操作...")
        command.append("--unshallow")
    print(f"  正在fetch仓库...{repo_Url}")
    # print(f"  命令：{command}")
    os.chdir(temp_dir)
    success, error_msg = run_command(command, 900)
    if not success:
        print(f"  {error_msg}")
        return False, error_msg
    print("  fetch 操作成功...")
    return True, ""
