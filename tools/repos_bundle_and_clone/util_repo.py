from datetime import datetime
import json
import os
import shutil
import stat
import tempfile


def save_to_json(org, all_repos, prefix):
    # 获取仓库信息
    # 生成带有日期的文件名
    current_date = datetime.now().strftime("%Y%m%d")
    script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repos")
    os.makedirs(script_dir, exist_ok=True)
    filename = os.path.join(script_dir, f"{prefix}_{org}_{current_date}.json")
    # 将仓库信息保存到JSON文件
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(all_repos, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved {len(all_repos)} repositories to {filename}")
    except Exception as e:
        print(f"Error saving to JSON file: {e}")


def read_repos_from_json(json_file_path: str) -> list[dict[str, str]]:
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
            repos.append(repo)
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
