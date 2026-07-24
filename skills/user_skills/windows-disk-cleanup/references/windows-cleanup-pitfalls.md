# Windows 磁盘清理 — 常见陷阱

## 编码问题：DISM 中文输出导致 Python subprocess 崩溃

**现象**：`subprocess.run(["Dism", ...])` 时，DISM 返回的中文文本（GBK/GB2312 编码）在 Python 默认 UTF-8 解码器下抛出 `UnicodeDecodeError`。

**错误信息**：
```
Exception in thread Thread-1 (_readerthread):
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xb2 in position 2: invalid start byte
AttributeError: 'NoneType' object has no attribute 'split'
```

**解决方案**：重定向输出到文件，绕过 subprocess 的自动解码
```python
out_file = "C:\\Users\\Admin\\AppData\\Local\\Temp\\dism.log"
subprocess.run(
    ["cmd", "/c", f"Dism ... > \"{out_file}\" 2>&1"],
    capture_output=True, timeout=300
)
with open(out_file, "r", encoding="utf-8", errors="replace") as f:
    content = f.read()
```

## 管理员权限问题

**现象**：DISM 和 cleanmgr /sagerun 需要管理员权限，Python subprocess 默认以非提权用户运行。

| 操作 | 是否需要管理员 | 替代方案 |
|------|--------------|---------|
| `Dism /online /Cleanup-Image /StartComponentCleanup` | ✅ 是 | 告知用户手动运行 |
| `cleanmgr /sagerun:1` | ✅ 是 | 无 sageset 预配置时不生效 |
| `cleanmgr /lowdisk /d C:` | 弹窗提权 | 启动 GUI，用户确认 |
| 清 Temp/缓存/回收站 | ❌ 否 | 可直接执行 |

## 回收站清空方法

```python
# 方法 1: PowerShell
subprocess.run(["powershell", "-Command", "Clear-RecycleBin -Force -Confirm:$false"])

# 方法 2: cmd（更可靠）
subprocess.run(["cmd", "/c", "rd /s /q C:\\$Recycle.Bin"], capture_output=True, timeout=10)
```

## 文件被占用时的处理

Temp 文件夹中部分 `.tmp` 文件被其他进程锁定（WinError 32），删除时捕获异常跳过即可：
```python
try:
    os.unlink(file_path)
except PermissionError:
    pass  # 文件正在使用，跳过
```

## pip/npm 缓存清理兜底

`pip cache purge` 和 `npm cache clean --force` 可能因 PATH 环境问题失败。直接删除缓存目录更可靠：
```python
import shutil
shutil.rmtree("C:\\Users\\Admin\\AppData\\Local\\pip\\cache", ignore_errors=True)
shutil.rmtree("C:\\Users\\Admin\\AppData\\Local\\npm-cache", ignore_errors=True)