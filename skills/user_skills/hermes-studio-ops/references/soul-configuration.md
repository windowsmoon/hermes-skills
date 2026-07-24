# SOUL.md 配置说明

## 概念区分（关键）

| 文件 | 控制什么 | 存储位置 |
|------|---------|---------|
| **SOUL.md** | **Agent 的性格/语气/行为方式**（我怎么说话、怎么思考） | `~/AppData/Local/hermes/SOUL.md`（默认 profile）|
| | | `~/.hermes/profiles/<name>/SOUL.md`（各 profile） |
| | | `~/AppData/Local/Hermes/SOUL.md`（Hermes Desktop GUI） |
| **User Profile** | **用户的画像/偏好/特征**（你是谁、你喜欢什么） | `memory(target='user')` 写入持久记忆 |
| **MEMORY** | **环境配置、踩坑记录、工具路径** | `memory(target='memory')` 写入持久记忆 |

**SOUL.md ≠ User Profile。** SOUL.md 定义 Agent 的角色人格；User Profile 定义用户本身的特征（MBTI、职业、偏好）。两者互不影响。

## SOUL.md 文件位置

| 范围 | 路径 | 说明 |
|------|------|------|
| 当前会话（default profile） | `~/AppData/Local/hermes/SOUL.md` | 当前对话中 Agent 的人格 |
| profile 专属 | `~/.hermes/profiles/<name>/SOUL.md` | 各 profile 独立人格 |
| Hermes Desktop GUI | `~/AppData/Local/Hermes/SOUL.md` | 桌面 GUI 设置的人格（不一定同步到 Agent） |

## 设置方式

### 方式一：直接编辑 SOUL.md 文件

SOUL.md 使用 Markdown 格式，内容决定 Agent 的行为方式。

```markdown
# 总体概括
You are Hermes Agent, ...

## 协作态度
- 原则 1: ...
- 原则 2: ...
```

### 方式二：Hermes Desktop GUI

桌面客户端的 Soul 模块提供预设模板（Teacher / Assistant / Critic 等），选择后写入 `~/AppData/Local/Hermes/SOUL.md`。

**注意**：Desktop GUI 的选择不一定会同步到 Hermes Agent 会话用的 `~/AppData/Local/hermes/SOUL.md`。如果 Desktop GUI 的设置不生效，检查两个文件是否一致。

### 方式三：Hermes Studio（不支持）

Hermes Studio v0.6.31 **没有** Soul/人格/角色设置的 UI 入口。侧边栏（任务/看板/频道/技能/插件/MCP/宠物/记忆/模型/日志/用量/性能监控/学习轨迹/技能用量/编程工具/版本预览/设备/用户/设置）中没有任何 Soul 相关选项。

修改 SOUL.md 只能通过文件编辑或 Desktop GUI。

## 各 Profile 的 SOUL.md 现状

| Profile | SOUL.md 存在 | 模型 |
|---------|-------------|------|
| default | `~/AppData/Local/hermes/SOUL.md` | deepseek-v4-flash |
| engineering-director | `~/.hermes/profiles/engineering-director/SOUL.md` | qwen3.7-plus |
| bigdata-director | `~/.hermes/profiles/bigdata-director/SOUL.md` | deepseek-v4-pro |
| operations-director | `~/.hermes/profiles/operations-director/SOUL.md` | minimax-m3 |
| product-manager | `~/.hermes/profiles/product-manager/SOUL.md` | deepseek-v4-pro |
| qa-director | `~/.hermes/profiles/qa-director/SOUL.md` | glm-5.2 |

## 常见问题

### Q: Desktop GUI 选了 Teacher，但 Agent 说话方式没变

A: 检查 `~/AppData/Local/Hermes/SOUL.md` 和 `~/AppData/Local/hermes/SOUL.md` 是否一致。Desktop GUI 写入的是前者，Agent 读取的是后者。如果不同，复制覆盖即可。

### Q: SOUL.md 和 User Profile 有什么区别？

A: SOUL.md = Agent 的性格。User Profile = 你的特征（MBTI、职业、偏好）。两者独立。
