# 三Agent决策门（最终版）

## 决策规则

```
收到用户任务后：
  │
  ├── 写代码/造工具/重构/开发功能 → 调 OpenCode（走 dev-pipeline-cli skill）
  │     └─ terminal("opencode '{需求}'")
  │
  ├── 已预置在 Coze 中的自动化工作流 → 调 Coze（走 coze-workflow-api skill）
  │     └─ 纯管道模式：调用 API 拿到数据直接返回，不加任何推理
  │
  ├── 部署/查日志/改配置/跑脚本 → Hermes 自己用 terminal 搞定
  │
  └── 其他 → Hermes 自己处理
```

## 重要规则

1. **Coze 是外挂插件箱**：调用 Coze 工作流时，不加自己的推理和思考，直接返回结果
2. **OpenCode 走 CLI**：不走 ACP 协议，通过 terminal 调用
3. **能用 terminal 搞定的，不调外部 Agent**
4. **识别 coze-workflow-api skill 的触发词**：当用户说"用扣子运行/执行"时，走 Coze 纯管道模式

## 三个 Agent 的定位

| Agent | 角色 | 做什么 | 通讯方式 |
|-------|------|--------|---------|
| Hermes | 大脑 + 协调器 | 决策、协调、简单操作（terminal） | 对话 + CLI |
| OpenCode | 码农 | 写代码、造工具、重构（TDD） | CLI（terminal 调用） |
| Coze | 外挂插件箱 | 执行已预置的自动化工作流 | HTTP API（纯管道输出） |

## 为什么用 Coze 而不是 Hermes skill

| 原因 | 说明 |
|------|------|
| Skill 调用有随机性 | 同 prompt 可能跑出不同结果 |
| 复杂 skill 浪费 token | 不如 Coze 工作流省 |
| Coze 插件不可复刻 | 不知道 API 地址、数据库结构 |
| 用户已在 Coze 做完思考 | Hermes 只需要取结果 |

## 完整流程示例

### 场景：写代码 + 部署

```
用户："帮我写一个监控脚本部署到服务器上"

Hermes 拆解：
  步骤1: 写代码 → 触发 dev-pipeline-cli skill
          → terminal("opencode '写一个Python内存监控脚本'")
  
  步骤2: 部署 → Hermes 自己用 terminal
          → terminal("scp file user@server:/path/")
          → terminal("ssh user@server 'systemctl restart service'")
```

### 场景：Coze 工作流

```
用户："用扣子处理这批客服消息"

Hermes：
  → 命中 coze-workflow-api skill
  → 调 Coze 工作流 stream_run API
  → 纯管道输出，不加推理
  → Interrupt → 暂停问用户 → Resume
  → Done → 直接输出结果
```