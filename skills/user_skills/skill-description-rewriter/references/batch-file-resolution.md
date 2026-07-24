# Batch File 解析实战记录

## 案例 1: skill_batch_6.json

> 来源：2026-07-21 尝试处理 `skill_batch_6.json` 的实战记录
> 问题：指定的 batch 文件不存在，terminal 工具不可用，最终无法完成任务

### 场景

父agent下发任务："重写 ~/skill_batch_6.json 中所有27个skill的description"

## 路径搜索清单（按优先级）

当 batch 文件路径为 `~/skill_batch_6.json` 时，尝试以下顺序：

| 优先级 | 路径 | 说明 |
|--------|------|------|
| 1 | `~/skill_batch_6.json` → `C:\Users\<user>\skill_batch_6.json` | `~` 展开 |
| 2 | 当前工作目录 + `skill_batch_6.json` | 同目录 |
| 3 | 父目录 `../skill_batch_6.json` | 上一级 |
| 4 | 常见的 `~` 展开变体 | 尝试 MSYS / cmd 风格 |
| 5 | `C:\Users\<user>\Desktop\` | 桌面 |
| 6 | `C:\Users\<user>\Downloads\` | 下载 |
| 7 | `C:\Users\<user>\AppData\Local\hermes\` | Hermes 数据目录 |
| 8 | 父agent的工作目录 | 本次为 `D:\Program\Hermes Studio\resources\webui` |

## 当文件不存在时的汇报格式

```markdown
## 无法完成任务 — 前置条件不满足

### 关键问题

**文件 `{path}` 不存在**

我已在以下所有路径搜索过，均未找到该文件：
- `{path1}` → 不存在
- `{path2}` → 不存在
- `{path3}` → 不存在
...

### 需要你（父agent）提供

请确认以下任一项：
1. **提供文件的实际路径** — 如果文件在另一个位置，请告诉我确切路径
2. **直接提供文件内容** — 将skill清单粘贴到消息中
3. **创建该文件** — 如果你知道这些skill是哪些，告诉我清单
```

## 替代方案：无 batch 文件时如何继续

### 方案A：从已安装 skill 中选

当 batch 文件不存在但 `skills_list` 可用时：

```
① skills_list 获取所有已安装 skill
② 向用户展示：[N] 个已安装 skill
③ 问用户：全部重写？选一批？指定名称？
④ 根据答复执行
```

### 方案B：从 batch 文件名推断

当 batch 文件名暗示了 skill 数量（如 `skill_batch_6.json` 暗示第6批），但文件不存在：

```
① 报告文件不存在
② 询问：是否要搜索历史会话中关于这批 skill 的提及？
③ 如果 session_search 有结果，用历史信息重建清单
④ 如果无结果，请用户提供清单
```

### 方案C：用户提供隐式清单

当用户说"重写 [文件名] 中所有 N 个skill"但文件不存在：

```
① 尝试 session_search 查找 batch 文件来源
② 检查父agent的上下文是否有隐含清单
③ 报告失败，附上所有尝试过的路径
④ 请求用户提供明确清单
```

## 关键教训

1. **不要假设 `~` 一定能正确展开** — Windows 上 `~` 可能指向 `C:\Users\<user>` 或 `/c/Users/<user>`，取决于 shell 上下文
2. **先查文件存在性再开始工作** — 路径解析是第一步，找不到直接汇报
3. **汇报时附上所有尝试过的路径** — 帮助父agent定位问题
4. **当 terminal 不可用时，用 read_file 替代** — 某些子agent环境中 terminal 可能不可用，但 read_file 仍可用
5. **session_search 可以查历史** — 如果 batch 文件是之前会话生成的，历史中可能有线索

## 案例 2: skill_batch_8.json

> 来源：2026-07-21 同一日第二次出现，尝试处理 `skill_batch_8.json` 的实战记录
> 问题：相同的 batch 文件不存在模式再次出现，确认这是上游父agent的重复性问题

### 场景

父agent下发任务："重写 ~/skill_batch_8.json 中所有23个skill的description"

### 执行过程

1. 按优先级搜索以下路径，均未找到文件：
   - `C:\Users\Admin\skill_batch_8.json` → ❌
   - `C:\Users\Admin\Desktop\skill_batch_8.json` → ❌
   - `C:\Users\Admin\Downloads\skill_batch_8.json` → ❌
   - `C:\Users\Admin\AppData\Local\hermes\skill_batch_8.json` → ❌
   - `D:\Program\Hermes Studio\resources\webui\skill_batch_8.json` → ❌
2. `session_search(query="skill_batch_8")` → 0 条结果
3. 按正确格式向父agent汇报，附上所有尝试过的路径

### 新增教训

| 教训 | 说明 |
|------|------|
| **检查相邻 batch 编号** | 当 `skill_batch_N.json` 不存在时，尝试检查 `skill_batch_N-1.json` 和 `skill_batch_N+1.json` 是否存在。如果均不存在，说明整个 batch 文件系列可能从未被实际写入磁盘，而是父agent在记忆中引用了不存在的文件 |
| **父agent上下文可能携带隐式清单** | 父agent的消息中可能直接包含了 skill 名称列表（如 "重写 unified-search, smart-ppt, ... 的 description"），无需依赖 batch 文件。检查父agent消息正文中是否包含逗号分隔或列举的 skill 名 |
| **第二次出现时应当升级处理** | 如果同一会话中已经处理过 `skill_batch_6.json` 不存在，现在 `skill_batch_8.json` 也不存在，说明这是上游父agent的系统性问题。应在汇报中明确指出"这已经是第二次遇到 batch 文件不存在的问题，建议父agent先创建文件再委托" |

### 新增推荐步骤

在 SKILL.md 的"当 batch 文件不存在时"流程中，增加以下步骤：

**步骤 2.5：检查相邻 batch 文件**

```python
# 当 skill_batch_N.json 不存在时，尝试 N-1 和 N+1
for adj in [N-1, N+1]:
    path = f"C:\\Users\\Admin\\Desktop\\skill_batch_{adj}.json"
    # 如果存在，说明 batch 文件确实在某个位置，只是命名偏移了
    # 如果不存在，说明整个 batch 系列从未写入
```

**步骤 2.6：检查父agent消息中的隐式清单**

```python
# 父agent的消息可能直接包含 skill 列表
# 如 "重写 ~/skill_batch_8.json 中所有23个skill的description"
# 检查消息正文中是否有逗号分隔的 skill 名称
# 或检查消息中是否有其他显式枚举
```