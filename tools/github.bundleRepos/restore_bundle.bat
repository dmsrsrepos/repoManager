@echo off
REM 从Git bundle文件恢复仓库的批处理脚本

echo Git Bundle恢复工具
echo =================

REM 检查参数
if "%~1"=="" (
    echo 错误: 缺少bundle文件路径参数
    echo 用法: restore_bundle.bat ^<bundle文件路径^> [输出目录]
    exit /b 1
)

set BUNDLE_FILE=%~1

REM 从bundle文件名提取仓库名称（去掉时间戳和.bundle扩展名）
for %%F in ("%BUNDLE_FILE%") do set FILE_NAME=%%~nF
for /f "tokens=1 delims=_" %%a in ("%FILE_NAME%") do set REPO_NAME=%%a

REM 如果没有提供输出目录，则使用仓库名称作为目录
if "%~2"=="" (
    set OUTPUT_DIR=.\%REPO_NAME%
) else (
    set OUTPUT_DIR=%~2
)

echo 使用Bundle文件: %BUNDLE_FILE%
echo 仓库名称: %REPO_NAME%
echo 输出目录: %OUTPUT_DIR%
echo.

REM 确保输出目录存在并初始化Git仓库
if not exist "%OUTPUT_DIR%" (
    mkdir "%OUTPUT_DIR%"
    echo 创建目录: %OUTPUT_DIR%
)

cd "%OUTPUT_DIR%"

REM 初始化Git仓库（如果不存在）
if not exist ".git" (
    echo 初始化Git仓库...
    git init
    if %ERRORLEVEL% NEQ 0 (
        echo 初始化Git仓库失败
        exit /b 1
    )
)

REM 从bundle文件中提取
echo 从bundle文件中提取...
git bundle unbundle "%BUNDLE_FILE%"
if %ERRORLEVEL% NEQ 0 (
    echo 从bundle文件提取失败
    exit /b 1
)

REM 列出可用的分支
echo.
echo 可用的分支:
git branch -a

REM 尝试检出主分支（可能是master或main）
echo.
echo 尝试检出主分支...
git checkout master 2>nul || git checkout main 2>nul || echo 无法自动检出主分支，请手动检出所需分支

echo.
echo 恢复完成! 仓库已恢复到: %OUTPUT_DIR%
echo 您可以使用 'cd %OUTPUT_DIR%' 进入仓库目录

pause