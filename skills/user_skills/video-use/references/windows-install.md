# video-use: Windows 安装指南

video-use 官方 install.md 偏向 macOS/Claude Code 环境。以下是在 **Windows + Hermes Agent** 环境下的完整安装步骤。

## 前置条件

| 组件 | 获取方式 |
|------|---------|
| git | Hermes 自带：`C:\Users\<user>\.hermes-web-ui\...\git\cmd\git.EXE` |
| uv | 已安装于 `~/.local/bin/uv.EXE` |
| Python 3.12 | Hermes 自带 或 `uv python` 自动管理 |
| ffmpeg | 从 gyan.dev 或 BtbN/FFmpeg-Builds 下载 |

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/browser-use/video-use.git ~/Developer/video-use
```

### 2. 安装 Python 依赖

```bash
cd ~/Developer/video-use
uv venv           # 创建虚拟环境
uv sync           # 安装依赖（requests, librosa, matplotlib, pillow, numpy）
```

验证依赖：

```python
# 用 .venv 的 Python 检查
.venv/Scripts/python.exe -c "import requests, librosa, matplotlib, PIL, numpy; print('OK')"
```

### 3. 安装 ffmpeg（Windows）

**方法：下载官方 build**

```bash
# 创建目录
mkdir -p ~/ffmpeg

# 下载 BtbN 的 ZIP build
# 手动访问: https://github.com/BtbN/FFmpeg-Builds/releases/latest
# 下载 ffmpeg-master-latest-win64-gpl.zip
# 解压后取出 bin/ffmpeg.exe 和 bin/ffprobe.exe

# 或用 Python 自动化（见下方）：
```

```python
import urllib.request, zipfile, shutil, os

ffmpeg_dir = os.path.expanduser("~/ffmpeg")
os.makedirs(ffmpeg_dir, exist_ok=True)
zip_path = os.path.join(ffmpeg_dir, "ffmpeg.zip")

url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
urllib.request.urlretrieve(url, zip_path)

with zipfile.ZipFile(zip_path, 'r') as zf:
    for name in zf.namelist():
        if name.endswith(('ffmpeg.exe', 'ffprobe.exe')):
            target = os.path.join(ffmpeg_dir, os.path.basename(name))
            with zf.open(name) as src, open(target, 'wb') as dst:
                shutil.copyfileobj(src, dst)
```

### 4. 加入 PATH

将 ffmpeg 目录复制到 Hermes 已有的 PATH 目录中（例如 `.../node/` 目录）：

```python
import shutil, os
ffmpeg_dir = os.path.expanduser("~/ffmpeg")
# 找 Hermes 所在的 PATH 目录
node_dir = "C:/Users/<user>/.hermes-web-ui/desktop-runtime/hermes/0.18.2/win-x64/node"
for exe in ["ffmpeg.exe", "ffprobe.exe"]:
    shutil.copy2(os.path.join(ffmpeg_dir, exe), os.path.join(node_dir, exe))
```

验证：`ffmpeg -version`、`ffprobe -version`

### 5. 注册为 Hermes Skill

```bash
# 复制到 Hermes skills 目录
$env:SKILLS = "$env:USERPROFILE\AppData\Local\hermes\skills"
Copy-Item -Recurse ~/Developer/video-use "$env:SKILLS\video-use"
```

或者用 Python：

```python
import shutil, os
src = os.path.expanduser("~/Developer/video-use")
dst = os.path.expanduser("~/AppData/Local/hermes/skills/video-use")
shutil.copytree(src, dst, ignore=shutil.ignore_patterns('.git', '.venv', '__pycache__'))
```

### 6. 设置 ElevenLabs API Key

```bash
cd ~/Developer/video-use
cp .env.example .env
# 编辑 .env，填入 ELEVENLABS_API_KEY=sk_xxxx
```

> ⚠️ `.env` 文件需要在两个位置：`~/Developer/video-use/.env`（运行时的 repo 根目录）和 `skills/video-use/.env`（技能目录）。也可以设环境变量 `ELEVENLABS_API_KEY`。

## Windows vs macOS 差异

| 方面 | macOS | Windows |
|------|-------|---------|
| Skill 注册 | `ln -sfn` 符号链接 | `Copy-Item -Recurse` 复制 |
| Python 环境 | 系统 Python + brew | uv + Hermes 自带 Python |
| ffmpeg | `brew install ffmpeg` | 手动下载 ZIP + 解压 |
| yt-dlp | `brew install yt-dlp` | `pip install yt-dlp` |
| `.env` 路径 | 只有 repo 根目录 | 需同步到 skills/ 目录 |
| 虚拟环境 | `.venv/` | `.venv/Scripts/`（注意路径差异） |

## 验证清单

```bash
# 1. 仓库存在
test -d ~/Developer/video-use && echo "OK"

# 2. Python 依赖
~/Developer/video-use/.venv/Scripts/python.exe -c "import requests, librosa, matplotlib, PIL, numpy; print('OK')"

# 3. ffmpeg
ffmpeg -version 2>&1 | head -1

# 4. ffprobe
ffprobe -version 2>&1 | head -1

# 5. Skill 注册
test -f ~/AppData/Local/hermes/skills/video-use/SKILL.md && echo "OK"

# 6. API Key
test -f ~/Developer/video-use/.env && grep ELEVENLABS_API_KEY ~/Developer/video-use/.env
```
