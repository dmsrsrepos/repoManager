import json


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
