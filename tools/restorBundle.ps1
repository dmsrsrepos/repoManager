<#
.SYNOPSIS
    恢复git镜像仓库（支持.gitbundle文件）
.DESCRIPTION
    本脚本用于将git bundle文件或远程镜像仓库的内容恢复到本地镜像仓库，
    保留完整的历史、分支和标签信息。适用于git clone --mirror创建的镜像仓库恢复。
.PARAMETER BundlePath
    git bundle文件的路径（如".\repo.bundle"）。若为空，则从远程URL恢复。
.PARAMETER RemoteUrl
    远程仓库的URL（如"https://github.com/username/repo.git"）。若BundlePath不为空，则优先使用Bundle文件。
.PARAMETER TargetMirrorPath
    本地目标镜像仓库的路径（如".\mirror_repo"）。若目录不存在，将自动创建。
.EXAMPLE
    PS> .\Restore-GitMirror.ps1 -BundlePath ".\repo.bundle" -TargetMirrorPath ".\mirror_repo"
    从repo.bundle文件恢复镜像仓库到.\mirror_repo目录
.EXAMPLE
    PS> .\Restore-GitMirror.ps1 -RemoteUrl "https://github.com/username/repo.git" -TargetMirrorPath ".\mirror_repo"
    从远程仓库恢复镜像仓库到.\mirror_repo目录
#>

param (
    [string]$BundlePath,
    [string]$RemoteUrl,
    [string]$TargetMirrorPath = ".\mirror_repo"
)

# 检查Git是否安装
function Test-GitInstalled {
    try {
        $gitVersion = git --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[INFO] Git已安装，版本：$gitVersion" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host "[ERROR] Git未安装，请先安装Git（https://git-scm.com/download/win）" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "[ERROR] Git命令未找到，请检查Git安装路径是否添加到系统环境变量" -ForegroundColor Red
        return $false
    }
}

# 验证Bundle文件的完整性与内容
function Test-GitBundle {
    param (
        [string]$BundlePath
    )
    Write-Host "[STEP 1/5] 验证Bundle文件：$BundlePath" -ForegroundColor Cyan
    
    # 检查文件是否存在
    if (-not (Test-Path -Path $BundlePath -PathType Leaf)) {
        Write-Host "[ERROR] Bundle文件不存在：$BundlePath" -ForegroundColor Red
        exit 1
    }
    
    # 验证Bundle完整性
    $verifyResult = git bundle verify $BundlePath 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Bundle文件损坏或不完整：" -ForegroundColor Red
        Write-Host $verifyResult -ForegroundColor Red
        exit 1
    }
    
    # 列出Bundle中的引用（分支/标签）
    Write-Host "[INFO] Bundle文件包含以下引用：" -ForegroundColor Green
    git bundle list-heads $BundlePath | ForEach-Object {
        Write-Host "  - $_" -ForegroundColor Green
    }
}

# 创建或初始化目标镜像仓库
function Initialize-TargetMirror {
    param (
        [string]$TargetPath
    )
    Write-Host "[STEP 2/5] 初始化目标镜像仓库：$TargetPath" -ForegroundColor Cyan
    
    # 如果目录不存在，则创建
    if (-not (Test-Path -Path $TargetPath -PathType Container)) {
        New-Item -ItemType Directory -Path $TargetPath | Out-Null
        Write-Host "[INFO] 创建目标目录：$TargetPath" -ForegroundColor Green
    }
    
    # 进入目标目录
    Set-Location -Path $TargetPath
    
    # 如果目录不是Git仓库，则初始化为空镜像仓库
    if (-not (Test-Path -Path ".git" -PathType Container)) {
        git init --bare | Out-Null
        Write-Host "[INFO] 初始化空的镜像仓库" -ForegroundColor Green
    }
    else {
        Write-Host "[INFO] 目标目录已经是Git镜像仓库" -ForegroundColor Green
    }
    
    # 返回上级目录（后续操作在上级目录进行）
    Set-Location -Path ..
}

# 恢复Bundle或远程仓库到目标镜像
function Restore-ToMirror {
    param (
        [string]$SourcePath,
        [string]$TargetPath
    )
    Write-Host "[STEP 3/5] 开始恢复内容到目标镜像仓库" -ForegroundColor Cyan
    
    # 进入目标镜像仓库目录
    Set-Location -Path $TargetPath
    
    try {
        if ($BundlePath) {
            # 从Bundle文件恢复
            Write-Host "[INFO] 从Bundle文件恢复..." -ForegroundColor Green
            git fetch $BundlePath | Out-Null
        }
        else {
            # 从远程仓库恢复
            Write-Host "[INFO] 从远程仓库恢复..." -ForegroundColor Green
            git remote add temp_origin $RemoteUrl | Out-Null
            git fetch temp_origin --tags | Out-Null
            git remote remove temp_origin | Out-Null
        }
        
        Write-Host "[INFO] 恢复完成" -ForegroundColor Green
    }
    catch {
        Write-Host "[ERROR] 恢复过程中出错：" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        exit 1
    }
    finally {
        # 返回上级目录
        Set-Location -Path ..
    }
}

# 验证恢复结果
function Test-RestoreResult {
    param (
        [string]$TargetPath
    )
    Write-Host "[STEP 4/5] 验证恢复结果" -ForegroundColor Cyan
    
    # 进入目标镜像仓库目录
    Set-Location -Path $TargetPath
    
    try {
        # 检查远程仓库配置（若有远程URL）
        $remoteConfig = git remote -v
        if ($remoteConfig) {
            Write-Host "[INFO] 远程仓库配置：" -ForegroundColor Green
            Write-Host $remoteConfig -ForegroundColor Green
        }
        else {
            Write-Host "[INFO] 未配置远程仓库（仅本地镜像）" -ForegroundColor Yellow
        }
        
        # 检查所有引用（分支/标签）
        Write-Host "[INFO] 目标镜像仓库中的引用：" -ForegroundColor Green
        git show-ref | ForEach-Object {
            Write-Host "  - $_" -ForegroundColor Green
        }
        
        # 检查提交历史（最新提交）
        $latestCommit = git log -1 --oneline
        Write-Host "[INFO] 最新提交：" -ForegroundColor Green
        Write-Host $latestCommit -ForegroundColor Green
    }
    catch {
        Write-Host "[ERROR] 验证过程中出错：" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        exit 1
    }
    finally {
        # 返回上级目录
        Set-Location -Path ..
    }
}

# 主流程
try {
    # 检查Git是否安装
    if (-not (Test-GitInstalled)) {
        exit 1
    }
    
    # 验证参数：至少需要BundlePath或RemoteUrl之一
    if (-not $BundlePath -and -not $RemoteUrl) {
        Write-Host "[ERROR] 必须提供BundlePath或RemoteUrl参数" -ForegroundColor Red
        exit 1
    }
    
    # 验证Bundle文件（若提供）
    if ($BundlePath) {
        Test-GitBundle -BundlePath $BundlePath
    }
    
    # 初始化目标镜像仓库
    Initialize-TargetMirror -TargetPath $TargetMirrorPath
    
    # 恢复内容
    Restore-ToMirror -SourcePath $BundlePath -TargetPath $TargetMirrorPath
    
    # 验证结果
    Test-RestoreResult -TargetPath $TargetMirrorPath
    
    Write-Host "[SUCCESS] 镜像仓库恢复完成！" -ForegroundColor Green
}
catch {
    Write-Host "[FATAL ERROR] 脚本执行失败：" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}