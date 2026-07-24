# GetPublicURL.ps1 — 右键获取阿里云OSS公开访问URL
# 右键文件 → GetPublicURL → 自动上传到OSS并复制公开URL到剪贴板
param(
    [Parameter(Mandatory=$true, Position=0, ValueFromPipeline=$true)]
    [string]$FilePath
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms

# === 配置 ===
$Bucket   = "windowsmoon"
$Endpoint = "oss-cn-shenzhen.aliyuncs.com"
$OssUrl   = "https://${Bucket}.${Endpoint}"
$ossutil  = "D:\Program\aliyun-ossutil\ossutil64.exe"

if (-not (Test-Path $FilePath)) {
    (New-Object -ComObject WScript.Shell).Popup("文件不存在: $FilePath", 0, "GetPublicURL", 0x10) | Out-Null
    exit 1
}

$FilePath = (Resolve-Path $FilePath).Path
$FileName = [System.IO.Path]::GetFileName($FilePath)
$FileSize = (Get-Item $FilePath).Length
$SizeStr  = if ($FileSize -gt 1MB) { "{0:N1} MB" -f ($FileSize/1MB) } else { "{0:N0} KB" -f ($FileSize/1KB) }

Write-Host "[GetPublicURL] Uploading: $FileName ($SizeStr)"

# === 上传到OSS ===
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName  = $ossutil
$psi.Arguments = "cp `"$FilePath`" `"oss://$Bucket/$FileName`""
$psi.UseShellExecute = $false
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError  = $true

$proc = New-Object System.Diagnostics.Process
$proc.StartInfo = $psi
$proc.Start() | Out-Null
$proc.WaitForExit()

$stdout = $proc.StandardOutput.ReadToEnd()
$stderr = $proc.StandardError.ReadToEnd()

if ($proc.ExitCode -ne 0) {
    Write-Host "[GetPublicURL] Upload failed: $stderr"
    (New-Object -ComObject WScript.Shell).Popup("上传失败 (Exit $($proc.ExitCode)):`n$stderr", 0, "GetPublicURL", 0x10) | Out-Null
    exit 1
}

Write-Host "[GetPublicURL] Upload OK"

# === 公开URL ===
$publicUrl = "$OssUrl/$FileName"

# === 复制到剪贴板 ===
[System.Windows.Forms.Clipboard]::SetText($publicUrl)

# 成功通知
(New-Object -ComObject WScript.Shell).Popup(
    "已上传并复制到剪贴板:`n$publicUrl",
    0, "GetPublicURL", 0x40
) | Out-Null

Write-Host "[GetPublicURL] Done: $publicUrl"
