import os
import shutil
import tempfile
import stat


def remove_readonly(func, path, _):
    """清除只读属性并重试删除操作"""
    os.chmod(path, stat.S_IWRITE)
    func(path)


search_dir = os.path.join(tempfile.gettempdir(), "repositoryMananger")

os.makedirs(search_dir, exist_ok=True)
prefix = "myRepository_"
suffix = "_gitRepo"
# 创建临时目录
temp_dir = tempfile.mkdtemp(prefix=prefix, suffix=suffix, dir=search_dir)
import stat

if __name__ == "__main__":
    for root, dirs, files in os.walk(search_dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                os.chmod(file_path, stat.S_IWRITE)  # 修改文件权限
                os.unlink(file_path)
                # print(f"已删除文件: {file_path}")
            except OSError as e:
                print(f"删除文件失败: {file_path}, 错误: {e}")
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            try:
                shutil.rmtree(dir_path, onerror=remove_readonly)  # 处理只读文件
            except OSError as e:
                print(f"删除目录失败: {dir_path}, 错误: {e}")
