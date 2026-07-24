# CLI 脚本安装说明

## 从哪里获取 edrawmind_cli.py

### 方式一：从 GitHub 下载（推荐）

```bash
# 直接下载 CLI 脚本
curl -o edrawmind_cli.py \
  https://raw.githubusercontent.com/wondershare-boop/edrawmind-skills/public/skills/edrawmind-mindmap/scripts/edrawmind_cli.py
```

### 方式二：通过 Hermes execute_code 下载

```python
import urllib.request, os
url = "https://raw.githubusercontent.com/wondershare-boop/edrawmind-skills/public/skills/edrawmind-mindmap/scripts/edrawmind_cli.py"
skill_dir = "C:/Users/Admin/AppData/Local/hermes/skills/content/edrawmind-mindmap/scripts"
os.makedirs(skill_dir, exist_ok=True)
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
resp = urllib.request.urlopen(req, timeout=30)
content = resp.read().decode("utf-8")
with open(os.path.join(skill_dir, "edrawmind_cli.py"), "w", encoding="utf-8") as f:
    f.write(content)
print(f"Downloaded {len(content)} bytes")
```

## 系统要求

- Python 3.8+（纯标准库，零依赖）
- 网络连接（调用云端 API）

## 验证安装

```bash
python scripts/edrawmind_cli.py --version
# → edrawmind-cli 1.0.0
```
