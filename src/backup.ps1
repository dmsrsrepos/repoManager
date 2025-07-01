<#
.SYNOPSIS
批量备份本地Git仓库的PowerShell脚本

.DESCRIPTION
扫描指定目录下的所有Git仓库，并为每个仓库创建bundle备份或镜像克隆

.PARAMETER SearchPath
要搜索Git仓库的根目录路径

.PARAMETER BackupMethod
备份方法："bundle"或"mirror"

.PARAMETER BackupRoot
备份文件存放的根目录
#>

param(
    [string]$SearchPath = "C:\Users\tangj15\OneDrive - Pfizer\Working File\Management\98 Source Code", # 默认搜索路径
    [ValidateSet("bundle", "mirror")]
    [string]$BackupMethod = "bundle", # 默认使用bundle方法
    [string]$BackupRoot = "C:\AppData\backup_code" # 默认备份目录
)

# 创建按日期命名的备份目录
$backupDir = Join-Path -Path $BackupRoot -ChildPath (Get-Date -Format "yyyyMMdd")
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

# 查找所有包含.git文件夹的目录
$gitRepos = Get-ChildItem -Path $SearchPath -Recurse -Hidden -Directory -Force | 
Where-Object { $_.Name -eq '.git' } | 
Select-Object -ExpandProperty FullName

if (-not $gitRepos) {
    Write-Host "在 $SearchPath 下未找到Git仓库" -ForegroundColor Yellow
    exit
}

Write-Host "找到 $($gitRepos.Count) 个Git仓库，开始备份..." -ForegroundColor Green

foreach ($gitDir in $gitRepos) {
    $repoPath = [System.IO.Path]::GetDirectoryName($gitDir)
    $repoName = [System.IO.Path]::GetFileName($repoPath)
    
    Write-Host "正在备份仓库: $repoName" -ForegroundColor Cyan
    
    try {
        if ($BackupMethod -eq "bundle") {
            # 使用git bundle创建备份
            $bundleFile = Join-Path -Path $backupDir -ChildPath "$repoName-$(Get-Date -Format 'yyyyMMdd-HHmmss').bundle"
            Set-Location -Path $repoPath
            git bundle create $bundleFile --all
            Write-Host "  → 创建bundle备份: $bundleFile" -ForegroundColor Green
        }
        else {
            # 创建镜像克隆
            $mirrorDir = Join-Path -Path $backupDir -ChildPath "$repoName.git"
            git clone --mirror $repoPath $mirrorDir
            Write-Host "  → 创建镜像克隆: $mirrorDir" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "  ! 备份失败: $_" -ForegroundColor Red
    }
}

Write-Host "备份完成! 备份存放在: $backupDir" -ForegroundColor Green