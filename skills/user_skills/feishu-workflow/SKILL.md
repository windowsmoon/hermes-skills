---
name: feishu-multimodal-params
description: >
  当用户需要从飞书多维表格读取数据/附件/URL，或写入数据时使用。
  支持：获取附件URL、读取记录、写入记录、批量操作。
  不要用于：飞书文档操作（走feishu-cli）、飞书消息推送（走飞书Bot）、非飞书的数据源。
  触发词：飞书、多维表格、bitable、从飞书获取、帮我处理飞书数据
triggers:
  - 生成图片
  - 生成视频
  - 制作视频
  - 飞书多维表格
  - 从飞书获取
  - 帮我处理飞书
  - bitable
  - 多模态
version: 1
tags:
  - feishu-workflow
  - feishu

---

# 多模态入参自动化（feishu-multimodal-params）

## 核心设计原则

**永远不要在用户没有确认入参之前就去读飞书表格。**

工作流分 6 步，每步必须等用户回复再进行下一步：

```
用户需求 → 询问入参 → 用户提供参数名 → 询问数据来源 → 用户提供来源 → 定位字段 → 生成
```

---

## 第 1 步：理解需求，询问入参

用户提出业务需求（如"帮我用这些素材生成视频"）。

**必须做的**：根据需求反推生成所需的最小参数集，向用户逐一确认。

**示例对话**：

> AI：好的，要生成视频，我需要确认几个参数：
> 1. **提示词 / 分镜描述**（必填）- 视频内容的文字描述
> 2. **参考图片**（可选）- 用于图生视频的图片
> 3. **音频**（可选）- 用于音视频混合的背景音乐/配音
> 
> 请告诉我你已有哪些参数？还是让我直接从飞书多维表格里读取？

---

## 第 2 步：用户提供参数名（或说"从飞书读取"）

用户可能：
- 提供具体参数名（如"分镜描述在飞书表格的「分镜描述」字段，图片在「图片」字段"）
- 说"从飞书读取"→ 跳到第 4 步

**参数分类**：
- **文本类**（直接读取，不需额外处理）：提示词、分镜描述、状态等
- **附件类**（需调用 `get_bitable_urls.py` 转 tmp_url）：图片、音频、视频
- **URL类**（直接使用）：视频URL、外部链接

---

## 第 3 步：用户确认参数名

记录参数名与字段的对应关系：

```
参数A → 字段名：XXX
参数B → 字段名：YYY
```

继续第 4 步。

---

## 第 4 步：询问数据来源

> AI：你说的这些字段数据从哪里获取？
> 
> 选项：
> A) 给我飞书多维表格 URL（我读取并列出所有记录，你选哪条）
> B) 直接给我这些字段对应的值（我直接用）

**如果用户选 A** → 第 4.1 步
**如果用户选 B** → 第 5 步（直接用值）

---

## 第 4.1 步：读取飞书多维表格 URL

用户给飞书多维表格 URL（如 `https://swi2cdl2nbg.feishu.cn/base/HeYWbu1Ppa2MEWs9AjJc09WJnce?table=tblEsoWpihj5JwM3`）。

**解析 URL** 提取：
- `app_token` = URL 中 base 后的部分（如 `HeYWbu1Ppa2MEWs9AjJc09WJnce`）
- `table_id` = URL 参数 `table=` 后的部分（如 `tblEsoWpihj5JwM3`）
- `view_id` = URL 参数 `view=` 后的部分（可选，用于筛选）

**通过 lark-cli 读取表格记录**：

```python
import subprocess, os, json

run_js = r"C:\Users\Admin\AppData\Roaming\npm\node_modules\@larksuite\cli\scripts\run.js"
env = os.environ.copy()
env["HERMES_HOME"] = r"C:\Users\Admin\AppData\Local\hermes"

# 读取所有记录（带字段名）
result = subprocess.run(
    ['node', run_js, 'base', '+record-list',
     '--base-token', app_token,
     '--table-id', table_id,
     '--limit', '100',
     '--format', 'json'],
    capture_output=True, text=True, timeout=30,
    cwd=r'D:\hermes-data', env=env
)
data = json.loads(result.stdout)
fields = data["data"]["fields"]          # ['序号', '图片', '音频', ...]
records = data["data"]["data"]          # [[values per record], ...]
record_ids = data["data"]["record_id_list"]

# 显示给用户
print("表格所有记录：")
for i, (rid, rec) in enumerate(zip(record_ids, records)):
    print(f"  [{i+1}] record_id={rid}")
    for fn, fv in zip(fields, rec):
        print(f"       {fn}: {str(fv)[:80]}")
    print()
```

**返回给用户**：

> AI：已读取表格，共 `{N}` 条记录（字段：`{字段列表}`）：
> 
> 请告诉我你要处理哪条记录？（输入序号 1-N）
> 
> | 序号 | 字段1 | 字段2 | ... |
> |------|-------|-------|------|
> | 1 | 值 | 值 | ... |
> | 2 | 值 | 值 | ... |

---

## 第 4.2 步：用户选择记录

用户输入序号（如 `3`）。

**定位具体记录**：

```python
idx = int(用户输入) - 1
selected_record = records[idx]
selected_record_id = record_ids[idx]
selected_fields = dict(zip(fields, selected_record))
print(f"选中记录: {selected_record_id}")
print(json.dumps(selected_fields, ensure_ascii=False, indent=2))
```

---

## 第 5 步：定位字段 + 提取数据

根据第 2-3 步确认的参数名 → 字段名映射，从选中的记录中提取数据。

**判断字段类型**（通过 tenant_access_token 获取字段 type）：

```python
import urllib.request, urllib.parse, json

def get_field_types(token, app_token, table_id):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read())
    return {f["field_name"]: f["type"] for f in result["data"]["items"]}

# type=17 为附件字段，需要调用 get_bitable_urls.py
# type=1/15 等为文本/URL 字段，直接读取
```

---

## 第 6 步：附件字段 → 调用 get_bitable_urls.py

对于所有 `type=17`（附件类型）的字段，调用脚本获取 tmp_url：

```python
import subprocess

result = subprocess.run(
    ['python',
     r'D:\hermes-data\get_bitable_urls.py',
     'cli_a851f4d520a8900b',
     '***FEISHU_SECRET***',
     app_token,
     table_id,
     selected_record_id],
    capture_output=True, text=True, timeout=60
)
urls_json = json.loads(result.stdout)
# urls_json = {"图片": ["文件名||url", ...], "音频": [...], "视频": [...], "_all_urls": {...}}
```

**将 JSON 格式化为可读输出**：

```python
for category in ["图片", "音频", "视频"]:
    items = urls_json.get(category, [])
    if items:
        print(f"\n## {category}")
        for item in items:
            name, url = item.split("||", 1)
            print(f"  - {name}: {url}")
```

**传给下游工具**：

```python
# 图片生成：取 urls_json["图片"] 中的 URL
for item in urls_json.get("图片", []):
    name, url = item.split("||", 1)
    # 调用 image_generate(prompt=..., reference_image_urls=[url])
    # 或 libtv upload + libtv node create --left <node>

# 音频：取 urls_json["音频"]
# 视频：取 urls_json["视频"]
```

---

## 已知多维表格参考

以下信息从用户 memory 中获取，无需重复确认，可直接使用：

| 名称 | app_token | table_id | 备注 |
|------|-----------|----------|------|
| LibTV自动化 | `HeYWbu1Ppa2MEWs9AjJc09WJnce` | `tblEsoWpihj5JwM3` | 图片/音频/视频均在 type=17 附件字段 |
| 巨量百应爆款视频 | `MMTVbJrRyaMkw6sNvT8cDj3Hnbe` | `tblCVaKtnnrXedDJ` | 全部字段为 type=1 文本，直接写字符串值，无需 `{"type":"text"}` 包装，批量写入用 batch_create |

---

## get_bitable_urls.py 脚本说明

**路径**：`D:\hermes-data\get_bitable_urls.py`

**入参**：
```
python get_bitable_urls.py <app_id> <app_secret> <app_token> <table_id> [record_id]
```

**出参**（stdout，JSON）：
```json
{
  "图片": ["文件名||tmp_download_url", ...],
  "音频": ["文件名||tmp_download_url", ...],
  "视频": ["文件名||tmp_download_url", ...],
  "_all_urls": {"文件名": "tmp_download_url", ...}
}
```

**关键参数**（写死在脚本中，通过 tenant_access_token 调用）：
- `app_id`: `cli_a851f4d520a8900b`
- `app_secret`: `***FEISHU_SECRET***`
- `extra`: `{"bitablePermission":"bitable_file_download_token"}`

**调用要点**：
- 每个 file_token 单独请求（批量请求返回空）
- 每次请求间隔 0.2s 防限流
- 用 `json.loads(stdout)` 解析输出

---

## 注意事项

1. **不要在用户确认前自动读表**：始终按第 1-6 步顺序执行，除非用户主动说"不需要确认，直接读表"
2. **多记录时必须让用户选**：不预设用哪条记录，让用户明确指定
3. **字段名语义匹配**：用户说"图片"时，自动匹配表格中含"图"/"photo"/"img"的字段名（不区分大小写）
4. **附件字段自动处理**：检测到 type=17 字段时，自动调用脚本，不需用户额外说明
5. **直接 URL 时跳过脚本**：如果用户已提供 tmp_url，直接传给工具，不重复调用脚本