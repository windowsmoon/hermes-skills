---
name: libtv-feishu-auto
description: >
  当用户需要从飞书多维表格读取分镜任务并自动生成LibTV画布时使用。
  自动化流程：飞书表格→读取分镜任务→LibTV生成→结果写回飞书。
  不要用于：手动操作LibTV（走libtv-cli）、非飞书数据源的LibTV生成。
  触发词：飞书LibTV、分镜自动化、LibTV自动生成、飞书分镜
tags: [libtv, feishu, automation, bitable, video, image]
triggers:
  - 飞书LibTV
  - 分镜自动化
  - LibTV自动生成
  - 飞书分镜

---

# LibTV × 飞书多维表格自动化

本 skill 从飞书多维表格读取分镜任务，**按任务性质独立执行**，不依赖 `libtv-cli` skill / `feishu-cli` skill。

## 核心设计原则

- **完全独立**：`libtv-cli` skill 损坏不影响本 skill 运行
- **任务独立**：图片任务和视频任务是两个独立入口，**互不依赖，不存在先行后续**
- **按任务性质分发**：每行记录根据「任务性质」字段决定走哪个生成路径
- **只读待处理**：只处理状态=待处理的行

---

## 一、飞书多维表格信息

| 项目 | 值 |
|---|---|
| 多维表格 | https://swi2cdl2nbg.feishu.cn/base/HeYWbu1Ppa2MEWs9AjJc09WJnce |
| App Token | `HeYWbu1Ppa2MEWs9AjJc09WJnce` |
| Table ID | `tblEsoWpihj5JwM3`（LibTV自动化） |
| LibTV 项目 | `a412891277714b22b8f902e948c4af4a` |

---

## 二、任务性质分发

| 任务性质 | 处理方式 | 使用的模型 | modeType |
|---|---|---|---|
| **生成分镜脚本** | ❌ 跳过（多维表格自动化处理） | — | — |
| **生成背景图** | ✅ 图片生成（text2image） | `Lib Navo 2` 或 `Lib Navo Pro` | `text2image` |
| **生成角色卡** | ✅ 图片生成（image2image） | `Lib Image`（默认）/ `Lib Navo 2` / `Lib Navo Pro` | `image2image` |
| **生成道具组图** | ✅ 图片生成（text2image） | `Lib Navo 2` 或 `Lib Navo Pro` | `text2image` |
| **生成分镜图** | ✅ 图片生成（image2image） | `Lib Image`（默认）/ `Lib Navo 2` / `Lib Navo Pro` | `image2image` |
| **生成视频片段** | ✅ 视频生成 | `Seedance 2.0 Mini`（默认）/ `2.0 VIP` / `2.0 Fast VIP` | `mixed2video` |

---

## 三、图片生成 — Lib Image / Lib Navo 2 / Lib Navo Pro

> 图片任务的 prompt 来源：优先「提示词」字段，无则「分镜描述」

### Lib Image（`lib-image-2`）— 支持 resolution 字段

| CLI 参数 | 必填 | 默认值 | 可选值 | 飞书字段 |
|---|---|---|---|---|
| `--prompt` | ✅ | — | 任意文字 | `提示词` / `分镜描述` |
| `model` | ✅ | — | `Lib Image` / `Lib Navo 2` / `Lib Navo Pro` | `图片_model` |
| `modeType` | ✅ | `image2image` | `image2image`（支持 0–10 张参考图） | `图片_modeType` |
| `count` | 否 | `1` | `1` / `2` / `4` | — |
| `ratio` | 否 | `auto` | `auto`、`1:1`、`1:2`、`2:1`、`9:16`、`16:9`、`3:4`、`4:3`、`3:2`、`2:3`、`5:4`、`4:5`、`21:9`、`9:21` | `图片_ratio` |
| `resolution` | 否 | `2K` | `1K` / `2K` / `4K` | `图片_resolution` |
| `quality` | 否 | `medium` | `low` / `medium` / `high` | — |

> `resolution` 和 `quality` 含义相近但独立：Lib Image 用 `resolution`；Navo 系列用 `quality`。

### Lib Navo 2（`nebula-2-flash`）& Lib Navo Pro（`nebula-ultra`）

| CLI 参数 | 必填 | 默认值 | 可选值 | 飞书字段 |
|---|---|---|---|---|
| `--prompt` | ✅ | — | 任意文字 | `提示词` / `分镜描述` |
| `model` | ✅ | — | `Lib Navo 2` / `Lib Navo Pro` | `图片_model` |
| `modeType` | ✅ | `image2image` | `image2image`（支持 0–7 张参考图） | `图片_modeType` |
| `count` | 否 | `1` | `1` / `2` / `4` | — |
| `ratio` | 否 | `16:9`（Navo 2）/ `16:9`（Navo Pro） | `auto`、`1:1`、`9:16`、`16:9`、`3:4`、`4:3`、`3:2`、`2:3`、`4:5`、`5:4`、`21:9` | `图片_ratio` |
| `quality` | 否 | `2K` | `1K` / `2K` / `4K` | `图片_resolution`（映射到 quality） |
| `searchable` / `search_enabled` | 否 | `0` | `0` / `1` | — |

**注意**：`Lib Navo 2` 的 `search_enabled`（联网搜索）、`Lib Navo Pro` 的 `searchable`；`Lib Image` 无此字段。

### CLI 命令示例

```bash
# text2image（无参考图，纯文字生图）
libtv node create "背景图-001" -t image \
  --prompt "赛博朋克城市夜景，高对比度" \
  -s "model=Lib Navo 2" \
  -s modeType=text2image \
  -s count=1 \
  -s ratio=16:9 \
  -s quality=2K \
  --run

# image2image（有参考图）
libtv node create "角色卡-001" -t image \
  --prompt "转换为动漫风格" \
  -s "model=Lib Image" \
  -s modeType=image2image \
  -s count=1 \
  -s ratio=16:9 \
  -s resolution=2K \
  --left "参考图-001" \
  --run
```

---

## 四、视频生成 — Seedance 2.0 Mini / VIP / Fast VIP

> 视频任务的 prompt 来源：优先「分镜描述」字段，无则「提示词」

### Seedance 2.0 Mini（`star-video2-mini`）

| CLI 参数 | 必填 | 默认值 | 可选值 | 飞书字段 |
|---|---|---|---|---|
| `--prompt` | ✅ | — | 任意文字 | `分镜描述` / `提示词` |
| `model` | ✅ | — | `Seedance 2.0 Mini` / `Seedance 2.0 VIP` / `Seedance 2.0 Fast VIP` | `视频_model` |
| `modeType` | ✅ | — | `singleImage2video`（需1图）/ `image2video`（需1-9图）/ `mixed2video`（需1-9图+0-3音）/ `frames2video`（需1-2图）/ `audio2video`（需0-3音）| `视频_modeType` |
| `count` | 否 | `1` | `1` / `2` / `4` | — |
| `ratio` | 否 | `16:9` | `adaptive`（Auto）/ `16:9` / `4:3` / `1:1` / `3:4` / `9:16` / `21:9` | `视频_ratio` |
| `resolution` | 否 | `720p` | `480p` / `720p` | `视频_resolution` |
| `duration` | 否 | `5` | 整数 4–15 | `视频_duration` |
| `enableSound` | 否 | `on` | `on` / `off` | `视频_enableSound` |
| `search_enabled` | 否 | `1` | `1` / `0` | `视频_search_enabled` |
| `autoCompliance` | 否 | `1` | `1` / `0` | — |

### CLI 命令示例

```bash
libtv node create "视频-001" -t video \
  --prompt "无人机掠过海面，日出时刻" \
  -s "model=Seedance 2.0 Mini" \
  -s modeType=mixed2video \
  -s count=1 \
  -s ratio=16:9 \
  -s resolution=720p \
  -s duration=5 \
  -s enableSound=on \
  -s search_enabled=1 \
  -s autoCompliance=1 \
  --left "参考图-001" \
  --left "音频-001" \
  --run
```

---

## 五、自动化流程

```
读取飞书多维表格，按顺序遍历每行
        ↓
  任务性质字段是否为空？
    ├─ 是 → 停止遍历，退出
    └─ 否 → 继续处理
        ↓
  每行根据「任务性质」分发（图片任务和视频任务完全独立）
        ↓
  ┌──────────────────────────────────────────────┐
  │ 生成分镜脚本 → 跳过（多维表格自动化处理）      │
  ├──────────────────────────────────────────────┤
  │ 生成背景图 / 生成道具组图（图片任务）          │
  │   → text2image，Lib Navo 2/Pro              │
  │   → prompt = 提示词                          │
  │   → 结果写入「图片URL」字段 + 「状态=完成」  │
  ├──────────────────────────────────────────────┤
  │ 生成角色卡 / 生成分镜图（图片任务）            │
  │   → image2image，Lib Image                   │
  │   → prompt = 提示词，上游图片作参考图          │
  │   → 结果写入「图片URL」字段 + 「状态=完成」  │
  ├──────────────────────────────────────────────┤
  │ 生成视频片段（视频任务）                       │
  │   → mixed2video，Seedance 2.0 Mini           │
  │   → prompt = 分镜描述，上游图+音频            │
  │   → 结果写入「视频URL」字段 + 「状态=完成」  │
  └──────────────────────────────────────────────┘
```

**遍历规则**：从第一条记录开始，逐行处理，**直到任务性质字段为空时停止**，不再处理后续记录。

**状态判断**（用中文文本，不用 option_id）：
- `状态 = 完成` → 跳过该行
- `状态 = 待处理 / 失败 / 进行中` → 执行处理

**生成结果写回规则**：

| 任务类型 | 生成成功写回 | 生成失败写回 |
|---|---|---|
| 生图任务（背景图/角色卡/道具组图/分镜图） | `图片URL` + `状态=完成` | `状态=失败` |
| 视频任务（生成视频片段） | `视频URL` + `状态=完成` | `状态=失败` |

---

## 六、自动化脚本

路径：`scripts/generate.py`

调试确认记录：直接记录在本文件第九节「技术要点」。

用法：
```bash
python scripts/generate.py
```

---

## 七、飞书 API（内嵌，不依赖 feishu-cli skill）

认证 App：`cli_a851f4d520a8900b` / `***FEISHU_SECRET***`

| 用途 | 端点 |
|---|---|
| 读取记录列表 | `GET /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records` |
| 更新记录 | `PUT /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}` |
| 附件下载链接 | `POST /open-apis/drive/v1/medias/batch_get_tmp_download_url` |

---

## 八、触发条件

用户说以下内容时触发：
- "从飞书自动生成"
- "运行 LibTV 自动化"
- "批量处理飞书多维表格"
- 任何提及飞书多维表格 + LibTV 任务的需求

---

## 九、技术要点（从实际调试中确认）

### 9.1 图片 / 视频任务的 prompt 来源规则

| 任务类型 | prompt 优先取 | 备用 |
|---|---|---|
| 图片任务（所有图片任务） | `提示词` 字段 | `分镜描述` |
| 视频任务（生成视频片段） | `分镜描述` 字段 | `提示词` |

### 9.2 modeType 正确对应任务类型

| 任务性质 | 正确 modeType | 常见错误 |
|---|---|---|
| 生成背景图 / 生成道具组图 | `text2image` | 误用 `image2image` |
| 生成角色卡 / 生成分镜图 | `image2image` | 误用 `text2image` |
| 生成视频片段 | `mixed2video`（需图片+音频上游） | 误用 `text2video`（该模型不支持） |

### 9.3 背景图/道具组图必须用 Lib Navo 2 或 Lib Navo Pro

这两个任务的 modeType 是 `text2image`，Lib Image 的 modeType.items 只有 `image2image`，不支持纯文字生图。脚本会自动强制覆盖为 `Lib Navo 2`。

### 9.4 模型专属参数字段名不同

| 模型 | 分辨率字段 | 联网搜索字段 | 默认 ratio |
|---|---|---|---|
| Lib Image | `resolution`（1K/2K/4K） | 无此字段 | `auto` |
| Lib Navo 2 | `quality`（1K/2K/4K） | `search_enabled` | `16:9` |
| Lib Navo Pro | `quality`（1K/2K/4K） | `searchable` | `16:9` |
| Seedance 2.0 Mini | `resolution`（480p/720p） | `search_enabled` | `16:9` |

### 9.5 飞书附件字段的结构

附件字段返回对象列表，每个对象含 `token`。获取下载链接：调用 `POST /open-apis/drive/v1/medias/batch_get_tmp_download_url`，body 传入 `file_tokens` 数组。

### 9.6 飞书单选字段的读取方式

单选字段（如 `任务性质`、`状态`）返回格式为 `{"text": "选项名"}`，需用 `fields.get("任务性质", {}).get("text")` 读取，不能直接 str()。

### 9.7 独立运行保障

`generate.py` 完全内嵌：所有 LibTV 模型参数、飞书 API 认证、field_id。`libtv-cli` skill 完全损坏时，只要 `libtv.exe` 程序正常，本 skill 仍可运行。

### 9.8 Seedance 2.0 Mini 不支持 text2video

该模型的 `modeType.items` 中没有 `text2video`。`generate.py` 默认使用 `mixed2video`，需要至少 1 张上游参考图。若图片字段为空，生成会失败。

### 9.9 `node create --run` 不会等待生成完成（两阶段模式）

**文档说** `--run` 会阻塞等待终态 JSON，但实际行为是：
- `libtv node create ... --run` 在节点创建后**立即返回**，stdout 只含 `newNodeKey`，不等待生成
- `stdout` 是多行格式化 JSON，按行 split 无法解析

**正确的两阶段做法**：
```python
# Step 1: 建节点（无 --run），从 stdout 解析 newNodeKey
rc, stdout, _ = libtv(["node", "create", node_name, ...])
data = json.loads(stdout.strip())        # 整体解析，不要按行 split
node_key = data["newNodeKey"]

# Step 2: 用 newNodeKey 触发生成并等待
rc, stdout, _ = libtv(["node", node_key, "-p", LIBTV_PROJ, "--run"])
compact = ''.join(stdout.split())        # 去掉换行后整体解析
data = json.loads(compact)
url = data.get("data", {}).get("url")     # 视频 URL 是数组
if isinstance(url, list): url = url[0]
```

### 9.10 `libtv upload` 输出也是多行 JSON

```python
# ❌ 错误：按行解析
for line in stdout.strip().split("\n"):
    data = json.loads(line)  # 失败

# ✅ 正确：整体解析
data = json.loads(stdout.strip())
node_key = data.get("nodeKey")
```

### 9.11 飞书附件 download URL 需要 Bearer token

飞书记录 API 返回的附件已含 `url` 字段，但直接 `urlretrieve` 会返回 400：
```python
req = urllib.request.Request(dl_url, headers={"Authorization": f"Bearer {token}"})
with urllib.request.urlopen(req) as resp:
    with open(local_path, "wb") as f:
        shutil.copyfileobj(resp, f)
```

### 9.12 附件 token 字段名是 `file_token`，不是 `token`

飞书记录 API 返回：`{"file_token": "xxx", "name": "xxx", "url": "..."}`

### 9.13 视频URL字段（type=15）写回格式

必须用 `{"link": url, "text": url}`，纯字符串报 `URLFieldConvFail`。

### 9.14 视频/图片附件字段（type=17）无法通过 URL 直接写入

附件字段需要 `file_token`，LibTV 生成的结果没有 file_token。**只写 URL 字段**，不写附件字段。

### 9.15 状态字段使用中文文本（已删除 option_id）

多维表格的选项值直接是文本：`待处理` / `进行中` / `完成` / `失败`，没有 option_id。
脚本中 `STATUS` 常量直接用中文：
```python
STATUS = {
    "pending": "待处理",
    "running": "进行中",
    "done":    "完成",
    "failed":  "失败",
}
```
判断跳过：`status_name == STATUS["done"]`（不能用 option_id）。

### 9.16 节点名用 record_id 前缀（支持覆盖/复用）

**旧策略**：每次加 uuid 后缀 → 同记录重复运行会创建多个同名不同后缀的节点，画布上垃圾节点越来越多，用户在网页版看到的不是最新结果。

**新策略（2026-07-08 确认）**：节点名 = `图片-{task_key}-{record_id[:8]}`
- 同一记录每次运行节点名固定，LibTV 检测到已存在时报错 `已存在显示名为"xxx"的节点`
- 进入覆盖流程：先删除旧节点，再创建新节点（保证干净状态）
- 资源节点名用 `REF-{record_id[:8]}-{task_key}-{N}` 格式，保证不与历史节点冲突

**效果**：飞书写回的 URL = 用户在网页版实际看到的那个节点的结果。

### 9.17 图片任务写回时必须同时更新状态

旧版只写 `图片URL` 字段，不写 `状态`，导致飞书显示「待处理」但实际已生成完成。
```python
update_record(token, record_id, {
    "图片URL": result_url,
    "状态": STATUS["done"]
})
```

### 9.18 连线必须用 nodeKey（UUID），不能用显示名

**旧策略**：`--left "素材-图-001-1"` 传显示名 → 当画布上有多个同名节点时，LibTV 会匹配到**最早创建的那个**（通常是空的），导致生成时没有参考图。

**新策略**：上传资源节点后记录返回的 `nodeKey`（UUID），连线时 `--left` 传 UUID。
```python
nk = libtv_upload(node_name, fpath, "image")   # 返回 nodeKey
resource_node_keys.append(nk)

# 连线时用 UUID
result_url = libtv_create_and_run(node_name, "image", prompt, params,
                                    lefts=resource_node_keys)  # 传的是 nodeKey UUID 列表
```

**验证**：
```bash
libtv node create "test" -t image --left <nodeKey-UUID>  # ✅ 用 UUID 可以正确连线
libtv node create "test" -t image --left "素材-图-001-1"  # ❌ 可能连到错误的同名节点
```

### 9.19 资源节点名也必须用 record_id 前缀

`libtv upload` 重复用同一显示名会创建**多个同名节点**（nodeKey 不同）。查询时 `libtv node "素材-图-001-1"` 可能匹配到空的旧节点。
```python
# ❌ 旧策略：同名节点堆积
node_name = f"素材-图-{counter:03d}-{i+1}"  # counter 会重复

# ✅ 新策略：用 record_id 前缀保证每次运行唯一
node_name = f"REF-{record_id[:8]}-{task_key}-{i+1}"  # 不冲突
```

### 9.20 节点查询用 display name 时 nodeKey 字段为 None

LibTV `node` 命令用显示名查询时，返回的 JSON 顶层 `nodeKey` 字段是 `null`，真正的 nodeKey 在 `data` 里。但用 UUID 直接查询时，顶层 `nodeKey` 正确返回。脚本需统一处理两种格式：
```python
data = json.loads(stdout.strip())
node_key = data.get("newNodeKey") or data.get("node", {}).get("nodeKey")
```

### 9.21 同名节点的 `upload` 会创建新 nodeKey 但不覆盖旧节点

`libtv upload "node-name" -f file.png` 重复执行会：
- 返回新 nodeKey（旧 nodeKey 仍然存在）
- `libtv node "node-name"` 行为不确定，可能匹配到任意一个

**结论**：不要用同名 upload。用 record_id 前缀保证唯一性（见 9.19）。