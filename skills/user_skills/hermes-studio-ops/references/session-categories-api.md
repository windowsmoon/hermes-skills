# 会话分类 API 详解

> Hermes Studio v0.6.32+ 支持会话分类管理

## 端点一览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/hermes/session-categories` | 列出所有分类 |
| POST | `/api/hermes/session-categories` | 创建分类 |
| DELETE | `/api/hermes/session-categories` | 删除分类 |
| GET | `/api/hermes/session-categories/{id}` | 获取单个分类 |
| PATCH | `/api/hermes/session-categories/{id}` | 重命名分类 |
| POST | `/api/hermes/sessions/{id}/category` | 设置会话分类 |
| DELETE | `/api/hermes/sessions/{id}/category` | 清除会话分类 |

## 会话列表中的分类信息

会话列表返回的每个 session 对象包含 `category_id` 字段：
- `null` — 未分类
- 数字 — 对应分类 ID

## 适用场景

- 按项目/功能/类型组织会话
- 快速过滤特定类别的对话记录
- 配合归档流程管理会话生命周期

## 标准操作流程

### 创建分类并归类会话

```
# 1. 创建分类
POST /api/hermes/session-categories
{"name": "分类名称"}
→ {"category": {"id": N, "name": "...", "created_at": ..., "updated_at": ...}}

# 2. 将已有会话归入该分类
POST /api/hermes/sessions/{session_id}/category
{"category_id": N}
→ {"ok": true, "category_id": N}

# 3. 查看所有分类
GET /api/hermes/session-categories
→ {"categories": [{"id": N, "name": "...", "created_at": ..., "updated_at": ...}]}
```

### 查找未分类会话

`GET /api/hermes/sessions?limit=50` 返回结果中过滤 `category_id: null` 的 session。

## 注意事项

- **同名分类不报错，但会创建新 ID** — 这是最大的坑！`POST /api/hermes/session-categories` 同名不报错，每次都返回 200 并创建一个新分类（不同 ID）。必须先 `GET /api/hermes/session-categories` 检查现有分类，有同名则用已存在的 ID，不要无脑 POST。
- `category_id: null` 表示清除分类
- 同一个 session 重复设置不同 category_id 会直接覆盖更新（幂等，多次调用不报错）
- **已结束的会话（`ended_at` 非 null）也能分类** — 分类不要求会话活跃，归档/已完成的会话同样可归类
- 分类删除后，已归入该分类的会话的 `category_id` 会？→ 待验证（推测变为 null）

## 实践记录

2026-07-22 (完整会话分类建设，三轮):

**第一轮：共创建 9 个分类、归类 13 个 Session：**

| ID | 分类名 | 归入 Session |
|:--:|--------|:---|
| 1 | Hermes内部功能 | `mrda3w8jd4s8cy` |
| 2 | 外部工具调试应用 | `3813bcd4-...`（当前会话） |
| 3 | 待调试功能 | `mrqfz8befcaper`、`mrqillm6y8pujm`、`20260708_134440_ac52fc` |
| 4 | 外部工具联系与通讯 | `mrq3re33tn8uqz` |
| 5 | 子Agent会话 | `74a03d61-...`、`9d420dc1-...`、`b9d84ec0-...` |
| 6 | 没想好/未处理的功能设定 | `mru45fddnj7est` |
| 7 | 自媒体 | `20260717_101712_6d09ec` |
| 8 | 主机电脑内部工具 | `mru1m5383hzfwi` |
| 9 | 外部智能硬件链接与工具 | `mrqid8oyatxd5q` |

**第二轮（补充）：又创建 1 个分类 + 2 个 Session**

| ID | 分类名 | 归入 Session |
|:--:|--------|:---|
| 10 | 外部多Agent链接与工具 | `mr9zun7ee8z1pd`, `mraf7pifl03cix` |

至此共 **10 个分类、15 个 Session** 已归档。

**第三轮（本会话）：补充 1 个分类 + 2 个 Session**

| ID | 分类名 | 归入 Session |
|:--:|--------|:---|
| 10 | 外部多Agent链接与工具 | `mr9zun7ee8z1pd`, `mraf7pifl03cix` |

至此共 **10 个分类、17 个 Session** 已归档（含本会话的多次分类调整）。

**关键经验补充（本会话第3轮实操验证）：**
- **分类切换**：同一 session 从分类 A 移到分类 B 只需 POST 新 category_id，旧分类自动解除（不需要先 DELETE）。已验证通过。
- **当前会话也可以分类**：正在对话中的 session（`ended_at: null`）分类无任何限制。

**用户交互模式（建立分类体系的典型对话流程）：**
```
用户: 创建分类 XXX
Agent: POST 创建 → 返回 ID

用户: 把 ID 为 aaa, bbb, ccc 放进去
Agent: 逐一 POST 归类（逐个执行，不等用户确认）

用户: 再创建 YYY，把 ID 为 ddd 放进去
Agent: 同时创建+归类
```
用户偏好：**直接给 ID 就立刻执行归类**，不需要先查一遍确认。多个 session 时逐个 POST 调用，不需要等用户说"都放进去"后再批量。

关键经验：
1. **先查再建** — 同名分类不会报错但会创建新 ID（第一次就踩了这个坑，以为同名会返回已有 ID，实际是新建）。前端用户说"创建"时务必先 GET 检查。
2. **批量归类** — 多个 session 归入同一分类时，每次 POST 都是独立的 HTTP 调用，且用户给一个就执行一个，不要攒起来等
3. **覆盖安全** — 同一个 session 反复设置不同 category_id 不会报错，直接覆盖
4. **已结束会话可归类** — 即便是 `ended_at` 已完成的旧会话也可以设置分类
5. 无「置顶会话」API — 会话列表返回中没有 is_pinned 字段，API 也没有 pin/unpin 端点。「置顶」可能是前端 Web UI 的本地行为，后端 API 层面无法区分置顶会话
6. memory 工具有硬性 10,000 字符限制 — Hermes 内置 memory 工具的 limit 是硬编码的 10,000 字符，无法通过配置调整。当用户说「记忆满了」时，只能通过批量清理（remove 旧条目 + add 新条目）来腾空间。这与 Hindsight 的 50,000 字符限制是两套不同的记忆系统。从 error 信息看 10k 是总存储上限，不是单条上限。
