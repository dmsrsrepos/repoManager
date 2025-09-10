import os
import subprocess


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


def fetch_repository(repo_Url: str, temp_dir: str) -> tuple[bool, str]:
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
