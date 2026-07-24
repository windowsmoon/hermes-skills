# LibTV × 飞书多维表格自动化 — 字段映射规范

本参考文档记录将飞书多维表格字段映射到 LibTV CLI 节点参数的规范，用于批量自动化生成场景。

**对应多维表格**（2026-07-08 最新确认）：
- App Token: `HeYWbu1Ppa2MEWs9AjJc09WJnce`
- 目标表: `LibTV自动化`（table_id: `tblEsoWpihj5JwM3`）
- 目标画布: `OpenAPI 默认项目`（projectId: `a412891277714b22b8f902e948c4af4a`，workspaceId: `226356`）

---

## 飞书多维表格现有字段

| field_id | 字段名 | 类型 | 说明 |
|---|---|---|---|
| fldm5skT1X | 序号 | AutoNumber | 自动编号 |
| fldSlaBSHs | 分镜描述 | Text | 镜头/分镜文字描述 |
| fldzAmcI8V | 图片 | Attachment (type=17) | 附件（含图片 URL） |
| fldqpoEqj1 | 音频 | Attachment (type=17) | 附件（含音频 URL） |
| fldr2UU4YN | 视频 | Attachment (type=17) | 附件（含视频 URL） |
| fldnm6sn3A | 提示词 | Text | 详细提示词 |
| fld6GP1N8t | 视频URL | Url | 视频链接 |
| fldvehN4ht | 状态 | SingleSelect | 待处理/进行中/完成/失败 |

---

## 生成流程（每行记录）

**第一步：图片生成**（分镜描述 + 提示词 → 图片）  
**第二步：视频生成**（所有字段 → 视频，参考图+音频+提示词混合）

---

## ⚠️ 节点命名规则（关键，避免踩坑）

### 节点名必须用 record_id 前缀

**旧策略（错误）**：节点名每次加 uuid 后缀，导致同名但不同节点的堆积，网页版默认显示旧节点，写回飞书的 URL 和用户看到的不一致。

**正确策略**：节点名 = `图片-{task_key}-{record_id[:8]}`，同一记录每次运行节点名固定。

**资源节点命名**：资源节点名 = `REF-{record_id[:8]}-{task_key}-{N}`，不使用通用的 `素材-图-{counter:03d}-{i+1}` 格式（counter 会重复，造成同名节点堆积）。

**旧节点已存在时的处理**：LibTV 检测到同名节点报错 `已存在显示名为"xxx"的节点` → 先删除旧节点，再创建新节点。不使用 update + run（因为 update + run 的逻辑复杂且易出错）。

### 连线必须用 nodeKey（UUID），不能用显示名

**旧策略（错误）**：`--left "素材-图-001-1"` 传显示名 → 当画布上有多个同名节点时，LibTV 会匹配到**最早创建的那个**（通常是空的或旧的），导致生成时参考图错误。

**正确策略**：上传资源节点后记录返回的 `nodeKey`（UUID），连线时 `--left` 传 UUID。
```python
nk = libtv_upload(node_name, fpath, "image")   # 返回 nodeKey
resource_node_keys.append(nk)
result_url = libtv_create_and_run(node_name, "image", prompt, params, lefts=resource_node_keys)
```

---

## 图片节点生成参数

### 必需字段（飞书多维表格补充）

| 建议字段名 | 类型 | 说明 |
|---|---|---|
| `图片_模型` | 单选 | 模型名字（modelName），如 `Lib Navo 2` |
| `图片_生成数量` | 数字 | 默认 1 |
| `图片_分辨率` | 单选 | 如 `2K`（Lib Navo 2 支持 1K/2K/4K） |
| `图片_比例` | 单选 | 如 `16:9`（见下表） |
| `图片_联网搜索` | 单选 | `是`/`否`，对应 `searchable=1`/`0` |

### 可用图片模型（2026-07-07 实际查询）

| modelKey | modelName（填入字段的值） | 说明 |
|---|---|---|
| `nebula-2-flash` | **Lib Navo 2** | 速度最快 ~25s，联网搜索 |
| `nebula-ultra` | **Lib Navo Pro** | 最强图片编辑，一致性好 |
| `lib-image-2` | **Lib Image** | 长文本能力突出 |
| `mj-v8.1` | **悠船 V8.1** | 美学提升，细节丰富 |
| `mj-v7` | **悠船 V7** | 最佳美学，电影质感 |
| `mj-niji7` | **悠船 Niji 7** | 动漫风格 |
| `jimeng-4.6` | **Seedream 4.6** | 人像一致性 |
| `seedream-5` | **Seedream 5.0 Lite** | 中式风格，联网 |

### 图片比例选项（nebula-2-flash）

`auto`、`1:1`、`9:16`、`16:9`、`3:4`、`4:3`、`3:2`、`2:3`、`4:5`、`5:4`、`8:1`、`1:8`、`4:1`、`1:4`、`21:9`

### CLI 命令模板（图片）

```bash
libtv node create "<节点名>" -t image \
  --prompt "<提示词>" \
  -s "model=<图片_模型>" \
  -s count=<图片_生成数量> \
  -s quality=<图片_分辨率> \
  -s ratio=<图片_比例> \
  -s searchable=<0或1> \
  --left <nodeKey-UUID> \
  --run
```

### 典型出图命令（Lib Navo 2）

```bash
libtv node create "图片-background-recvoG9i" -t image \
  --prompt "赛博朋克风格城市夜景" \
  -s "model=Lib Navo 2" \
  -s count=1 \
  -s quality=2K \
  -s ratio=16:9 \
  -s searchable=1 \
  --run
```

---

## 视频节点生成参数

### 必需字段（飞书多维表格补充）

| 建议字段名 | 类型 | 说明 |
|---|---|---|
| `视频_模型` | 单选 | 模型名字，如 `Seedance 2.0 VIP` |
| `视频_生成数量` | 数字 | 默认 1 |
| `视频_生成模式` | 单选 | modeType，如 `mixed2video` |
| `视频_比例` | 单选 | 如 `16:9` |
| `视频_分辨率` | 单选 | 如 `720p`（480p/720p/1080p/4k） |
| `视频_时长(秒)` | 数字 | 4–15 整数 |
| `视频_音频` | 单选 | `开启`/`关闭` → `on`/`off` |

### 可用视频模型（2026-07-07 实际查询）

| modelKey | modelName（填入字段的值） | 说明 |
|---|---|---|
| `star-video2` | **Seedance 2.0 VIP** | 最强视频，15s，音画同步 ✅推荐默认 |
| `star-video2-fast` | **Seedance 2.0 Fast VIP** | 同上快速版 |
| `star-video2-mini` | **Seedance 2.0 Mini** | 高性价比 |
| `kling-v3-omni` | **Kling O3** | 视频编辑，一致性，音画同出，多镜头 |
| `kling-v3-turbo` | **Kling 3.0 Turbo** | 高质感，支持多镜头 |
| `happy-horse-1.1` | **Happy Horse 1.1** | 阿里最新，一致性更可控 |

### modeType（视频生成模式）选项

| modeType 值 | 说明 | 需要的上游资源 |
|---|---|---|
| `text2video` | 文生视频 | 仅 prompt，无上游 |
| `singleImage2video` | 单图生视频 | 需 1 张参考图 |
| `image2video` | 图片参考 | 需 1–9 张参考图 |
| `mixed2video` | **混合模式** ✅推荐 | 图片 1–9 + 音频 0–3 + 视频 0–3 |
| `frames2video` | 首尾帧 | 需 1–2 张参考图 |
| `video2video` | 视频参考 | 需参考视频 |
| `audio2video` | 音频驱动 | 需 1–3 个音频 |

### 视频比例选项（star-video2）

`adaptive`（Auto）、`16:9`、`4:3`、`1:1`、`3:4`、`9:16`、`21:9`

### 视频分辨率选项（star-video2）

`480p`、`720p`（默认）、`1080p`、`4k`

### 时长范围（star-video2）

整数 4–15 秒，默认 5 秒

### CLI 命令模板（视频，混合模式）

```bash
libtv node create "<节点名>" -t video \
  --prompt "<分镜描述或提示词>" \
  -s "model=<视频_模型>" \
  -s modeType=mixed2video \
  -s count=<视频_生成数量> \
  -s ratio=<视频_比例> \
  -s resolution=<视频_分辨率> \
  -s duration=<视频_时长(秒)> \
  -s enableSound=<on或off> \
  -s search_enabled=1 \
  --left <nodeKey-UUID> \
  --left <nodeKey-UUID> \
  --run
```

---

## 自动化工作流

1. 读取飞书多维表格每行记录（通过 tenant_access_token API）
2. 对 `状态=待处理` 的行：
   - 上传图片/音频附件作为 LibTV 资源节点（节点名用 `REF-{record_id[:8]}-{task_key}-{N}` 格式）
   - 用返回的 `nodeKey` 连线（不用显示名）
   - 用分镜描述/提示词作为 prompt
   - 将生成的图片/视频 URL 回填到飞书多维表格的 `图片URL`/`视频URL` 字段
   - 同时更新 `状态` 为 `完成`（漏写状态是常见 bug）

### 获取附件 URL 的两种方式

| 方式 | 优点 | 缺点 |
|------|------|------|
| 记录中已有 `url` 字段 | 直接可用 | 下载时需 Bearer token |
| `batch_get_tmp_download_url` API | 可获取临时下载链接 | 步骤更多 |

**推荐流程**：直接从记录附件对象取 `url` 字段，但下载时加 `Authorization: Bearer {token}` header。

## 飞书 API 端点参考

```bash
# 列出多维表格
GET /open-apis/bitable/v1/apps/{app_token}/tables

# 获取表字段
GET /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields

# 读取记录
GET /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records

# 更新记录
PUT /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}
```