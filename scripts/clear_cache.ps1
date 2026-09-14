<#
.SYNOPSIS
    Clear AI Video Producer Studio caches, topic deduplication vault, and test renders.

.DESCRIPTION
    Resets the persistent topic memory vault (storage/topic_memory_vault.json),
    clears user storage renders, resets database state, and removes __pycache__
    and .pytest_cache artifacts so you can test again and again with clean state.

.PARAMETER UserId
    Optional user ID to clear only that user's topic memory and storage renders.
    If omitted, clears all cache across the entire studio.

.EXAMPLE
    .\scripts\clear_cache.ps1
    .\scripts\clear_cache.ps1 -UserId user_krishna_01
#>

[CmdletBinding()]
param(
    [string]$UserId = ""
)

$ErrorActionPreference = "SilentlyContinue"

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "             CLEARING STUDIO CACHES & DEDUPLICATION TOPICS             " -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$StorageDir = Join-Path $ProjectRoot "storage"
$VaultFile = Join-Path $StorageDir "topic_memory_vault.json"
$DbFile = Join-Path $StorageDir "db_state.json"

# 1. Clear Topic Memory Vault (Deduplication topics)
Write-Host "`n[*] Clearing Topic Memory Deduplication Vault..." -ForegroundColor Yellow
if (Test-Path $VaultFile) {
    if ($UserId -and $UserId.Trim() -ne "") {
        try {
            $Content = Get-Content $VaultFile -Raw | ConvertFrom-Json
            $Filtered = @()
            $RemovedCount = 0
            foreach ($Item in $Content) {
                if ($Item.user_id -and ($Item.user_id -eq $UserId -or $Item.user_id -eq "user-$UserId")) {
                    $RemovedCount++
                } else {
                    $Filtered += $Item
                }
            }
            $Filtered | ConvertTo-Json -Depth 10 | Set-Content $VaultFile -Encoding UTF8
            Write-Host "    -> Cleared $RemovedCount deduplication topic(s) for user '$UserId'." -ForegroundColor Green
        } catch {
            Write-Host "    -> Error filtering vault: $_" -ForegroundColor Red
        }
    } else {
        # Full reset
        "[]" | Set-Content $VaultFile -Encoding UTF8
        Write-Host "    -> Reset storage/topic_memory_vault.json to empty list []." -ForegroundColor Green
    }
} else {
    "[]" | Set-Content $VaultFile -Encoding UTF8
    Write-Host "    -> Initialized fresh storage/topic_memory_vault.json." -ForegroundColor Green
}

# 2. Clear Rendered Episodes & Storage Caches
Write-Host "`n[*] Clearing Rendered Episodes and Storage Caches..." -ForegroundColor Yellow
if ($UserId -and $UserId.Trim() -ne "") {
    $UserClean = $UserId.Replace("_", "-").ToLower()
    $UserDirs = Get-ChildItem -Path $StorageDir -Directory -Filter "*$UserClean*" -ErrorAction SilentlyContinue
    foreach ($Dir in $UserDirs) {
        Remove-Item -Path $Dir.FullName -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "    -> Removed storage folder: $($Dir.Name)" -ForegroundColor Green
    }
} else {
    $AllUserDirs = Get-ChildItem -Path $StorageDir -Directory -Filter "user-*" -ErrorAction SilentlyContinue
    $DirCount = 0
    foreach ($Dir in $AllUserDirs) {
        Remove-Item -Path $Dir.FullName -Recurse -Force -ErrorAction SilentlyContinue
        $DirCount++
    }
    Write-Host "    -> Removed $DirCount user render storage folder(s)." -ForegroundColor Green
}

# 3. Clear DB State (Projects / Episodes / Shows)
if (-not $UserId -or $UserId.Trim() -eq "") {
    Write-Host "`n[*] Resetting Database State (storage/db_state.json)..." -ForegroundColor Yellow
    if (Test-Path $DbFile) {
        Remove-Item -Path $DbFile -Force -ErrorAction SilentlyContinue
        Write-Host "    -> Cleared storage/db_state.json for fresh testing." -ForegroundColor Green
    }
}

# 4. Clear Python __pycache__ and bytecode
Write-Host "`n[*] Clearing Python bytecode caches (__pycache__, *.pyc)..." -ForegroundColor Yellow
$PycacheDirs = Get-ChildItem -Path $ProjectRoot -Directory -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue
$PycCount = 0
foreach ($Dir in $PycacheDirs) {
    Remove-Item -Path $Dir.FullName -Recurse -Force -ErrorAction SilentlyContinue
    $PycCount++
}
Write-Host "    -> Cleaned $PycCount __pycache__ director(ies)." -ForegroundColor Green

# 5. Clear Pytest Cache
Write-Host "`n[*] Clearing Pytest Cache (.pytest_cache)..." -ForegroundColor Yellow
$PytestCache = Join-Path $ProjectRoot ".pytest_cache"
if (Test-Path $PytestCache) {
    Remove-Item -Path $PytestCache -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "    -> Cleared .pytest_cache." -ForegroundColor Green
}

# 6. Clear Temporary Scratch Files
$ScratchDir = Join-Path $ProjectRoot "scratch"
if (Test-Path $ScratchDir) {
    Get-ChildItem -Path $ScratchDir -File -Filter "test_*" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host "    -> Cleaned temporary scratch test files." -ForegroundColor Green
}

Write-Host "`n========================================================================" -ForegroundColor Cyan
Write-Host "               ALL CACHES & TOPIC MEMORY CLEARED!                       " -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "Ready for fresh automated testing and interactive video synthesis.`n" -ForegroundColor White
