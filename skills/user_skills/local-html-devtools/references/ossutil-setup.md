# ossutil 右键菜单工具 — 阿里云 OSS 上传

## 状态（2026-07-08 ✅ 完成）

所有组件已就位，右键菜单已恢复正常工作。

## 注册表信息

```
HKEY_CURRENT_USER\Software\Classes\*\shell\GetPublicURL
    (默认) = GetPublicURL
    Icon = C:\Users\Admin\AppData\Local\hermes\scripts\oss-upload.ico

HKEY_CURRENT_USER\Software\Classes\*\shell\GetPublicURL\command
    (默认) = powershell.exe -ExecutionPolicy Bypass -File "C:\Users\Admin\AppData\Local\hermes\scripts\GetPublicURL.ps1" %1
```

## 已安装文件

| 文件 | 路径 | 说明 |
|------|------|------|
| ossutil64.exe | `D:\Program\aliyun-ossutil\ossutil64.exe` | v1.7.17 Windows PE |
| GetPublicURL.ps1 | `C:\Users\Admin\AppData\Local\hermes\scripts\GetPublicURL.ps1` | 右键脚本 |
| oss-upload.ico | `C:\Users\Admin\AppData\Local\hermes\scripts\oss-upload.ico` | 右键图标 |
| .ossutilconfig | `C:\Users\Admin\.ossutilconfig` | ossutil 凭证配置 |

## OSS Bucket 配置

| 字段 | 值 |
|------|-----|
| Bucket 名 | windowsmoon |
| 外网 Endpoint | oss-cn-shenzhen.aliyuncs.com |
| 文件访问 URL | `https://windowsmoon.oss-cn-shenzhen.aliyuncs.com/<filename>` |
| CNAME | windowsmoon.cn-shenzhen.taihangtop.cn（需CDN控制台配置，未生效） |

## ossutil 下载试错记录

| URL | 结果 | 说明 |
|-----|------|------|
| `gosspublic/1.7.19/ossutil64` | 404 | 版本不存在 |
| `gosspublic/1.7.18/ossutil64` | 200 → **Linux ELF** ❌ | 无后缀 URL = Linux ELF |
| `gosspublic/1.7.18/ossutil64.exe` | 404 | Windows .exe 不存在 |
| `gosspublic/1.7.17/ossutil64` | 200 → **Windows PE** ✅ | magic=4d5a |

**规律**：ossutil 1.7.18+ 无后缀 URL 统一返回 Linux ELF；Windows 版需无后缀 URL 碰巧有 PE 版本（1.7.17 是最后一个）；加 `.exe` 后缀的版本均不存在。

## GetPublicURL.ps1 工作原理

1. 接收右键传来的文件绝对路径 `$FilePath`
2. 用 `Process` 对象调用 `ossutil cp` 上传到 `oss://windowsmoon/文件名`
3. 生成公开 URL：`https://windowsmoon.oss-cn-shenzhen.aliyuncs.com/文件名`
4. `Clipboard.SetText()` 复制到剪贴板 + 弹窗通知

**关键**：必须用 `System.Diagnostics.Process` 显式传参，**禁止** `Invoke-Expression`（路径含空格会断裂）。