---
name: hermes-studio-ops
description: >-
  Hermes Studio 运营管理 —— 会话管理（归档/分类/检索）、会话数据库操作、
  备份恢复、Kanban看板、多Agent架构、插件管理、配置管理、版本升级。
  覆盖 Web UI API 操作和底层文件操作。
  不要用于：普通对话、开发任务、搜索信息。
  触发词：归档会话、会话管理、会话分类、sessions.db、kanban、备份、看板
triggers:
  - 归档会话
  - 会话管理
  - 会话分类
  - sessions.db
  - kanban
  - 备份
  - 看板
tags:
  - hermes-studio-ops
  - hermes

---

# Hermes Studio Ops

## 概述

Hermes Studio 运营管理技能。涵盖 Web UI API 和底层文件两个层面的运维操作。

## 能力矩阵

### 1. 会话管理

#### 1.1 会话分类（Category）

通过 Hermes Studio API 管理会话分类标签：

```bash
# 列出所有分类（先查再建，避免重复创建同名分类）
GET /api/hermes/session-categories

# 创建分类
POST /api/hermes/session-categories
{"name": "分类名称"}

# 为会话设置分类
POST /api/hermes/sessions/{session_id}/category
{"category_id": 1}

# 清除会话分类
DELETE /api/hermes/sessions/{session_id}/category
```

返回格式示例：
```json
{
  "category": {
    "id": 1,
    "name": "Hermes内部功能",
    "created_at": 1784688661,
    "updated_at": 1784688661
  }
}
```

**推荐流程（用户交互时）：**
1. 先 `GET /api/hermes/session-categories` 列出已有分类，告诉用户哪些已存在
2. 用户说创建 → 再 `POST` 创建
3. 用户指定 Session → 逐个 `POST .../sessions/{id}/category` 归类
4. 用户说"全部放进去"意味着多个 session 归同一个分类，需要逐个调用

**典型问答模式（用户对话中）：**
- 用户说"创建分类 XXX" → 先查有没有同名，没有再创建
- 用户说"把 ID 为 ... 的放进去" → 立刻 POST 归类，不需要再确认
- 用户说"归到 XX 分类" → 需要知道分类 ID（先查）→ 直接归类
- 用户一次给多个 session ID → **逐个立即执行归类**，不等用户确认再批量
- 用户说"再创建 YYY，把 ZZZ 放进去" → 两步连续执行，中间不停顿
- 用户说"把 XXX 分类的会话改成 YYY" → 直接 POST 新 category_id，旧分类自动解除（已验证）
- 当前正在对话的 session 也能分类（已验证）
- **核心原则（2026-07-22 验证）：用户给 ID 就是指令，直接执行，不需要再确认**\n\n**记忆工具限制：** `memory` 工具有硬性 10,000 字符总上限（非 Hindsight 限制），无法通过配置调整。超过时需用 `operations` 批量 remove 旧条目腾空间。Hindsight 有独立 50,000 字符限制，但 daemon 需要完整 Python stdlib 支持。

**注意事项（详见 reference）：**
- ⚠️ **同名分类不报错，会创建新 ID** — 这是最大的坑！不检查直接 POST 会建出多个"相同名字"但不同 ID 的分类
- 已结束的会话也能分类
- 切换分类只需 POST 新 ID，不需要先 DELETE 旧的
- **没有"置顶会话"的 API** — 会话列表无 is_pinned 字段，也无 pin/unpin 端点

#### 1.2 会话归档

- 自动归档脚本：`scripts/archive_sessions.py`
- 通过 Web UI 的归档功能
- 已导出的会话存放在 `D:/hermes-data/conversation/`

#### 1.3 会话检索

- 通过 `session_search` 工具按关键词/日期/Profile 检索
- 支持跨 Profile 只读查询

### 2. Kanban 看板

（保留原有 Kanban 架构参考）

#### 2.1 Kanban 增强（kanban-enhancer）

从 2026-07-24 起，Kanban 增加了 4 项外围增强能力（通过 `devops/kanban-enhancer` skill 实现，不修改核心代码）：

| 增强项 | 文件 | 功能 |
|--------|------|------|
| 工具亲和性检查 | `scripts/tool_affinity.py` | 分派任务时检查 Profile 是否有对应工具 |
| 结果标准化 | `kanban_enhancer.py` (内置) | 强制 result 字段为 JSON 格式 |
| 失败升级链 | `kanban_enhancer.py` (内置) | 失败任务自动跨 Profile 升级 |
| 验证门禁 | `scripts/verification_gate.py` | 关键任务完成后自动生成验证子任务 |

**调度方式**：cron job 每 5 分钟轮询 Kanban DB（SQLite 只读），状态文件 `~/.kanban-enhancer-state.json` 防重复处理。

**数据源**：`D:/Obsidian/Note/Profile能力矩阵.md` 提供工具-Profile 映射表。

> 详见 `devops/kanban-enhancer` skill

### 3. 备份与恢复

（保留原有备份参考）

### 4. Profile 管理

#### 4.1 创建新 Profile（API 方式）

通过 Hermes Studio API 创建 Profile 并配置模型和 SOUL：

```bash
# 1. 创建 Profile（必填 name）
POST /api/hermes/profiles
{"name": "designer"}

# 2. 写入 SOUL.md（到 ~/AppData/Local/hermes/profiles/{name}/SOUL.md）
#    来源可以是 agency-agents-zh（~500个角色，含设计/工程/产品等）
#    agency-agents-zh 路径：~/Developer/agency-agents-zh/ 或 ~/AppData/Local/hermes/cache/agency-agents-zh/
#    设计类角色在 design/ 目录下

# 3. 配置 config.yaml（到 ~/AppData/Local/hermes/profiles/{name}/config.yaml）
memory:
  provider: hindsight
default_provider: custom:gemini
default_model: gemini-3.5-flash
custom_providers:
  custom:gemini:
    api_key: YOUR_KEY
    base_url: https://generativelanguage.googleapis.com
    api_mode: chat_completions
toolsets:
  - hermes-cli
  - web
  - file
  - terminal

# 4. 配置 .env（到 ~/AppData/Local/hermes/profiles/{name}/.env）
GEMINI_API_KEY=YOUR_KEY

# 5. 复制技能到新 profile（可选）
cp -r ~/AppData/Local/hermes/skills/{skill_name} ~/AppData/Local/hermes/profiles/{name}/skills/
```

**Profile 目录结构**：每个 Profile 在 `~/AppData/Local/hermes/profiles/{name}/` 下有：
- `config.yaml` — 模型/Provider 配置
- `.env` — 环境变量/API Key
- `SOUL.md` — 角色人格定义
- `skills/` — 该 Profile 可用的技能
- `sessions/` — 该 Profile 的会话
- `memories/` — 该 Profile 的记忆

**agency-agents-zh 角色库**（jnMetaCode/agency-agents-zh）：
- ~500 个 AI 角色配置，含设计/工程/产品/运营/法律/金融等
- 每个角色有完整的 YAML frontmatter + Markdown 人格描述
- 设计类角色：`design/design-ui-designer.md`、`design-ux-architect.md`、`design-ux-researcher.md` 等
- 已克隆到 `~/Developer/agency-agents-zh/`
- 已有 5 个现有 Profile 的 SOUL 通过此仓库增强

**典型流程（用户对话中）：**
- 用户说"新增一个 XXX Profile" → 先 POST 创建 → 写 SOUL.md → 配 config.yaml → 复制 skills
- 用户说"参考 agency-agents-zh 里面的 XX 角色" → 去该仓库对应目录找 SOUL 文件
- 创建后不用切换 Profile，通过 delegate_task 派任务过去

#### 4.2 配置 Auxiliary Models（Vision/生图/生视频）

通过 API 配置 Hermes 的辅助模型（非对话类任务专用）：

```bash
# 查看当前配置
GET /api/hermes/config/auxiliary-models

# 更新 vision 模型（只传要改的 key，其他保持原值）
PUT /api/hermes/config/auxiliary-models
{
  "auxiliary": {
    "vision": {
      "provider": "custom:gemini",
      "model": "gemini-3.5-flash",
      "timeout": 120
    }
  }
}
```

支持的任务类型：`vision`、`image_generation`、`video_generation`、`web_extract` 等。
详见 `references/auxiliary-models-api.md`。

### 5. Windows 文件操作

当 `write_file`、`read_file`、`terminal` 工具因编码问题失败时，使用 Hermes Studio API 作为替代方案：

```bash
# 读取文件
GET /api/hermes/files/read?path=C:\Users\Admin\AppData\Local\hermes\memories\MEMORY.md

# 写入文件
PUT /api/hermes/files/write
{
  "path": "C:\\Users\\Admin\\AppData\\Local\\hermes\\memories\\MEMORY.md",
  "content": "文件内容..."
}
```

> 详见 `references/windows-file-operations.md`

### 6. 版本升级

（保留原有版本参考）

## 参考文件\n\n- `references/kanban-architecture.md` — Kanban 架构详解\n- `references/session-categories-api.md` — 会话分类 API 详情\n- `references/hermes-python-env-fix.md` — Hermes 配套 Python 环境修复 + Hindsight 安装\n- `references/backup-migration.md` — 备份恢复\n- `references/config-keys.md` — 配置键说明\n- `references/soul-configuration.md` — SOUL 配置
- `references/auxiliary-models-config.md` — 辅助模型（Vision/生图等）API 配置
- `references/zhihu-search-setup.md` — 知乎搜索 CLI + MCP 安装配置
- `references/windows-file-operations.md` — Windows 文件操作编码问题 workaround
