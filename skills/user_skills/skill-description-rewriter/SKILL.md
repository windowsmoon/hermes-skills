---
name: skill-description-rewriter
description: >
  当用户要求重写某个skill的description时使用。
  按照三条原则（入口治理/手册治理/错误治理）重写description，加上边界条件和触发词。
  不要用于：修改skill正文内容、新建skill、删除skill。
  触发词：重写description、改一下描述、这个skill的描述不符合标准
tags:
  - skill-governance
  - description
  - entry-governance
triggers:
  - 重写description
  - 改一下描述
  - 这个skill的描述不符合标准

---

# Skill Description 重写工具

## 触发条件

用户说以下任一：
- "重写 [skill名] 的 description"
- "帮我改一下 [skill名] 的描述"
- "这个 skill 的 description 不符合标准"
- "检查所有 skill 的 description"
- "批量重写 [N]个 skill 的 description"
- "重写 [文件名] 中所有 skill 的 description"

**重要：当任务明确提到"三条原则"或"三条原则重写description"时，agent 应首先加载本 skill**（`skill_view(name="skill-description-rewriter")`），因为"三条原则"是此 skill 的核心方法论。不要跳过此步骤直接开始执行。

## 标准格式

### Description 模板

```yaml
description: >
  当 [触发条件1] 且 [触发条件2] 时使用。
  用于 [具体任务描述]。
  不要用于 [排除场景1]、[排除场景2]。
  触发词：[触发词1]、[触发词2]、[触发词3]
```

### 三条原则自检清单

重写后对照：

- [ ] **入口治理**：只看名字和描述，能否判断什么时候该用、什么时候不该用？
- [ ] **手册治理**：正文是否包含四类信息（输入条件、执行步骤、判断分支、失败处理）？
- [ ] **错误治理**：之前的纠错有没有沉淀回 skill？

## 重写流程

### 手动重写（用户偏好方案A）

这是用户明确选择的方案：**每次对话中手动逐个重写，品质最高但慢。** 不要尝试批量API重写，不要用subagent委托批量处理。

```
用户：重写 unified-search 的 description
  ↓
① 找到 skill 路径：skills_list 查看 category，路径为
   ~/AppData/Local/hermes/skills/<category>/<skill-name>/SKILL.md
  ↓
② 读取 SKILL.md，提取当前 description（YAML frontmatter 中的 description 字段）
  ↓
③ 分析当前 skill 的用途和场景
  ↓
④ 按标准格式重写 description（加上边界条件、排除场景、触发词）
  ↓
⑤ 直接更新 SKILL.md（用户不需要确认，直接改）
  ↓
⑥ 同步更新飞书表格的触发词和概率
```

### 飞书表格同步

每次重写一个skill的description后，同时更新飞书审计表的记录。

触发概率按以下规则计算（2026-07-21 用户纠正）：

| 触发词特征 | 概率 | 例子 |
|-----------|------|------|
| 包含唯一标识（域名/符号/专有名词） | 95% | `v.douyin.com` → 抖音分析skill |
| 包含明确动作意图（帮我×/开发/修复/生成） | 75% | `用扣子运行` → Coze工作流skill |
| 通用意图（分析/对比/搜索/评估） | 60% | `模型对比` → 模型评估skill |
| 模糊意图（帮我做/需要××/通用词） | 40-50% | `帮我做` → 可能匹配多个skill |

**核心原则：** 触发概率反映的是「触发词的唯一性和精确度」，不是触发词的数量。用户一条Prompt里面通常只有一个触发意图，所以概率衡量的不是"有几个触发词"，而是"这个词有多大概率正确命中这个skill"。

飞书表格URL：`https://swi2cdl2nbg.feishu.cn/base/NoZVbWlR4ahbQesNGFKcStw9n5d`

### 批量重写（从 batch 文件）

```
用户：重写 skill_batch_1.json 中所有 skill 的 description
  ↓
① 读取 batch JSON 文件，解析 skill 列表
  ↓
② 验证每个 skill 的 SKILL.md 路径是否存在
  ↓
③ 逐 skill 读取当前 description（从 YAML frontmatter）
  ↓
④ 按标准格式重写每条 description
  ↓
⑤ 一次性展示所有新旧对比，让用户确认
  ↓
⑥ 确认后逐条更新（skill_manage action=patch）
  ↓
⑦ 输出对比表和触发词列表
```

### Batch 文件格式规范

batch JSON 文件应包含一个数组，每个元素包含 skill 名称和（可选）路径：

```json
[
  {"name": "skill-name-1"},
  {"name": "skill-name-2", "path": "可选/绝对/路径/SKILL.md"}
]
```

不传 path 时，agent 自动从 skills_list 查找 category 并拼出路径：
`~/AppData/Local/hermes/skills/<category>/<skill-name>/SKILL.md`

### 当 batch 文件不存在时

如果用户指定的 batch 文件不存在，**不要直接放弃**，按以下步骤处理：

#### 1. 全面路径搜索

尝试以下路径解析顺序（Windows 环境）：

| 优先级 | 路径解析 | 说明 |
|--------|---------|------|
| 1 | `~/{filename}` → `C:\Users\<user>/{filename}` | `~` 展开 |
| 2 | 当前工作目录 `./{filename}` | 同目录 |
| 3 | 当前工作目录父级 `../{filename}` | 上一级 |
| 4 | `C:\Users\<user>\Desktop\{filename}` | 桌面 |
| 5 | `C:\Users\<user>\Downloads\{filename}` | 下载 |
| 6 | `C:\Users\<user>\AppData\Local\hermes\{filename}` | Hermes 数据目录 |
| 7 | 父agent当前工作目录（task 中可推断） | 如 `D:\Program\Hermes Studio\resources\webui` |

所有路径用 `read_file` 工具验证，不要依赖 terminal 的路径查找。

#### 2. 搜索历史会话

```python
session_search(query = "{batch_filename}")
```
如果 batch 文件是之前会话生成的，历史中可能有线索（如文件内容、skill 清单、生成时间）。

#### 2.5 检查相邻 batch 编号

当 `skill_batch_N.json` 不存在时，尝试检查 `skill_batch_{N-1}.json` 和 `skill_batch_{N+1}.json` 是否存在：

```python
for adj in [N-1, N+1]:
    read_file(f"C:\\Users\\Admin\\skill_batch_{adj}.json")
    read_file(f"C:\\Users\\Admin\\Desktop\\skill_batch_{adj}.json")
```

- 如果相邻文件存在 → 说明 batch 文件确实在某个位置，但命名偏移了，可参考其格式推断
- 如果相邻文件也不存在 → 说明整个 batch 系列从未写入磁盘，这是上游父agent的系统性问题

#### 2.6 检查父agent消息中的隐式清单

父agent的消息正文中可能直接包含了 skill 名称列表，无需依赖 batch 文件：

```python
# 检查父agent消息中是否有逗号分隔的 skill 名称列表
# 例如 "重写 unified-search, smart-ppt, xhs-cli 的 description"
# 或 "23个skill的名称是：unified-search, smart-ppt, ..."
```
如果发现隐式清单，直接提取并继续执行，无需等待父agent回复。

#### 3. 确认文件不存在后汇报

用以下格式向父agent报告：

```
## 无法完成任务 — 前置条件不满足

### 关键问题

**文件 {path} 不存在**

我已在以下所有路径搜索过，均未找到该文件：
- {path1} → 不存在
- {path2} → 不存在
...

### 需要你（父agent）提供

请确认以下任一项：
1. **提供文件的实际路径**
2. **直接提供文件内容**（将skill清单粘贴到消息中）
3. **创建该文件**（告诉我清单，我来创建）
```

#### 4. 替代方案

如果父agent无法提供 batch 文件：

- **方案A**：用 `skills_list` 获取所有已安装 skill，询问用户是否从中选一批
- **方案B**：从 batch 文件名推断（如 `skill_batch_6.json` 暗示第6批），用 `session_search` 查找历史线索
- **方案C**：询问父agent"你有隐含的skill清单吗？"

## 触发词概率评估标准（2026-07-21 用户纠正）

**核心原则：** 触发概率反映的是「触发词的唯一性和精确度」，不是触发词的数量。
用户一条 Prompt 里面通常只有一个触发意图，所以概率衡量的不是"有几个触发词"，而是"这个词有多大概率正确命中这个skill"。

| 触发词特征 | 概率 | 例子 |
|-----------|------|------|
| **包含唯一标识**（域名/符号/专有名词/版本号） | 95% | `v.douyin.com` → 抖音分析skill |
| **包含明确动作意图**（帮我×/开发/修复/生成） | 75% | `用扣子运行` → Coze工作流skill |
| **通用意图**（分析/对比/搜索/评估） | 60% | `模型对比` → 模型评估skill |
| **模糊意图**（帮我做/需要××/通用词） | 40-50% | `帮我做` → 可能匹配多个skill |

**错误示范（不要用）：**
- 按触发词数量算概率（4个词=80%，2个词=60%）← 用户说这是错的
- 按匹配类型算概率（精确匹配=100%，语义相近=80%）← 太泛

**正确做法：** 分析每个触发词的特征，取最高概率的那个词作为最终概率。

## 常见陷阱

| 陷阱 | 说明 | 避免方法 |
|------|------|---------|
| **路径猜错** | 假设 skill 在固定 category 下，但实际在别的 category | 先 `skills_list` 确认 category，再拼路径 |
| **忘记读当前 description** | 直接重写而不看 SKILL.md 中当前的 YAML frontmatter description | 步骤②必须提取当前 description 做对比基准 |
| **只写能力不写边界** | 重写后的 description 只描述"能做什么"，不写"什么时候不该用" | 每一条 description 必须有排除场景（"不要用于..."） |
| **遗漏触发词** | 重写后没有列出触发词 | 对照 skill 正文，提取3-5个最可能触发该 skill 的关键词 |
| **batch 文件不存在时不处理** | 找不到文件就放弃，不尝试 fallback | 用全面路径搜索 + `skills_list` + `session_search` 多管齐下，然后向父agent汇报 |
| **一次性改太多不确认** | 批量重写时直接改完不展示对比 | 每批改完先展示新旧对比，让用户确认后再执行 |
| **batch 文件名暗示数量但文件不存在** | 如 `skill_batch_6.json` 暗示27个skill，但文件不存在，agent 不知道是哪些skill | 先全面搜索路径，用 `session_search` 查历史，再向父agent报告"文件不存在，请提供清单" |
| **重复出现 batch 文件不存在** | 同一会话中已处理过 batch_N 不存在，现在 batch_M 又不存在，说明是上游问题 | 在汇报中明确标注"第 N 次出现此问题"，建议父agent先创建文件再委托；同时检查相邻 batch 编号和父agent消息中的隐式清单 |

## 参考文档

- `references/batch-file-resolution.md` — 批量重写时 batch 文件找不到的实战处理记录