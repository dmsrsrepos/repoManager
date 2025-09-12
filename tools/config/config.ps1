git config --global core.longpaths true
git config --global http.postBuffer 1048576000

#作用：将 VS Code 设置为 Git 的默认编辑器（需安装 VS Code）。
git config --global core.editor 'code --wait' 

# Windows 用户设置为 true ，自动将换行符转换为 CRLF 。
git config --global core.autocrlf true

#禁用文件名大小写忽略（避免因大小写问题导致文件重复）。
git config --global core.ignorecase false

# 作用：
# preloadindex 和 fscache ：加速文件状态检查。
# gc.auto ：自动清理松散对象的阈值（默认 6700，调整为 256 更频繁清理）。
git config --global core.preloadindex true
git config --global core.fscache true
git config --global gc.auto 256

git config --global user.name 'calmripple'
git config --global user.email 'calmripple@dmsrs.org'