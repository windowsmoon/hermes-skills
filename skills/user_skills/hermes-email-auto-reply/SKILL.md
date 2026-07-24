---
name: hermes-email-auto-reply
description: >
  当用户需要hermes-email-auto-reply时使用。
  不要用于：无关场景。
  触发词：自动回复邮件、邮件自动回复、邮件Pipeline
tags: [email, imap, fork, session, 腾讯企业邮箱, oss, 阿里云]
related_skills:
  - hermes-studio-ops
triggers:
  - "邮件接收"
  - "email接收"
  - "腾讯企业邮箱"
  - "IMAP 轮询"
  - "邮件 Fork"
  - "邮件转CLI"
  - "邮件自动回复"
  - "email platform"
  - "邮箱自动回复"
  - "邮件配置"
  - "email配置"
  - "邮件附件"
  - "邮件图片"
  - "邮箱附件OSS"
---
# Hermes Email Receive Pipeline

腾讯企业邮箱接收 → Hermes Studio 可对话 session 的完整管道。

## 架构总览

```
┌───────────────────────────────────────────────┐
│ email_receiver.py（独立守护进程）              │
│   IMAP 轮询（30秒）→ 收件                      │
│   提取正文 + 图片 → 保存到本地                  │
│   提取附件 → 保存本地 + 上传阿里云 OSS          │
│   无LLM · 无SMTP · 纯接收                      │
├───────────────────────────────────────────────┤
│ fork_session_monitor.py（独立守护进程）        │
│   监控 DB（5秒）→ 发现 email session           │
│   → Fork 为 CLI session + 结构化邮件摘要        │
│   → 附件显示为可点击的 OSS URL                  │
│   → 图片标注本地路径（可 vision_analyze）       │
└───────────────────────────────────────────────┘
```

### 关键设计决策

| 决策 | 原因 |
|------|------|
| 不用 Gateway email 插件 | 插件是"即用即走"自动回复设计，无法设为纯接收模式。用户明确拒绝自动回复 |
| 两段分离而非一个脚本 | 收件（IMAP）和 Fork（DB监控）是两个不同职责，分离后任一可独立替换 |
| 直接写 DB 而非调 API | Hermes API 无法向当前 session 推送消息。直接写 `hermes-web-ui.db` 是唯一可靠方案 |
| 附件上传阿里云 OSS | 已有 ossutil 配置，桶 windowsmoon 公网可读 |
| 图片存本地不自动分析 | 避免在收件阶段消耗 LLM 费用，用户需要时可 vision_analyze |

## 第一步：收件（email_receiver.py）

**路径**: `D:\Program\Hermes Studio\relate program\email_receiver.py`

### 配置（脚本顶部常量）

| 项目 | 值 |
|------|-----|
| 邮箱 | `maizhiyi@gzfuyaozhishang.com` |
| IMAP 服务器 | `imap.exmail.qq.com:993`（SSL）|
| 授权码 | `Lvwx7aV236RibpFm`（客户端授权码，≠登录密码）|
| 轮询间隔 | 30 秒 |
| OSS 桶 | `windowsmoon`（`oss-cn-shenzhen`）|
| ossutil | `D:\Program\aliyun-ossutil\ossutil64.exe` |

### 收到邮件后的动作

1. IMAP FETCH → 解析 Subject / From / Date / 正文
2. **提取图片**（image/jpeg, png, gif 等）→ 保存到 `email_images/{session_id}/`，路径写入消息
3. **提取附件**（非 image 的带 filename 的 MIME 部分）：
   a. 保存到 `email_attachments/{session_id}/`
   b. 通过 ossutil 上传到 `oss://windowsmoon/email_attachments/{session_id}/{filename}`
   c. 生成公网 URL: `https://windowsmoon.oss-cn-shenzhen.aliyuncs.com/email_attachments/{session_id}/{filename}`
4. 写 `hermes-web-ui.db`：`sessions` + `messages`（一条 user 消息，含结构化全文 + 附件URL + 图片路径）
5. 标记 SEEN
6. **不做任何其他事**（无 LLM、无 SMTP、无通知）

### 消息内容格式例

```
收到一封邮件，请帮我处理：

**邮件主题**: Fwd: 项目方案及预算
**发件人**: pm@corp.com
**时间**: Thu, 9 Jul 2026 15:00:00 +0800

**邮件正文**:
（邮件正文内容）

附件:
- [方案书_v2.docx](https://windowsmoon.oss-cn-shenzhen.aliyuncs.com/email_attachments/xxx/方案书_v2.docx)
- [预算表.xlsx](https://windowsmoon.oss-cn-shenzhen.aliyuncs.com/email_attachments/xxx/预算表.xlsx)

图片:
- C:\Users\Admin\AppData\Local\hermes\email_images\xxx\photo_1.jpg
---
```

### 模式

| 参数 | 作用 |
|------|------|
| (无参数) | 持续轮询守护进程 |
| `--once` | 单次检查新邮件后退出 |

### 启动/停止

```bash
# 手动后台启动
"C:\Users\Admin\.hermes-web-ui\desktop-runtime\hermes\0.18.0\win-x64\python\python.exe"
  "D:\Program\Hermes Studio\relate program\email_receiver.py"

# 测试连接
...python.exe" "D:\...\email_receiver.py" --once

# 停止
taskkill /F /FI "IMAGENAME eq python.exe" /FI "CMDLINE like '%email_receiver%'"
```

### 调试

- 日志: `C:\Users\Admin\AppData\Local\hermes\email_receiver.log`
- IMAP 轮询: 每 30 秒检查 UNSEEN
- OSS 上传成功日志: `OSS upload ok: xxx.pdf -> https://...`
- 已处理 UID 记录: `C:\Users\Admin\AppData\Local\hermes\email_receiver_state.json`

## 第二步：Fork 为 CLI session

由 `fork_session_monitor.py` 处理。

**路径**: `D:\Program\Hermes Studio\relate program\fork_session_monitor.py`

### 行为

- 每 5 秒扫描 `hermes-web-ui.db` 中新 `source='email'` 的 session
- 创建 `source='cli'` 的新 session（Web UI 显示输入框 ✅）
- 复制原消息内容
- **添加 MSG1（role='assistant'）**: 结构化摘要，含附件可点击 URL
- 标题加 `[邮件]` 前缀
- 用 `fork_state.json` 追踪已处理的 session ID，避免重复

### Fork 后的 session 结构

```
[邮件] Fwd: 项目方案及预算 - AI平台建设
├── MSG0 [user]: 原始邮件内容（含 OSS 附件 URL）
└── MSG1 [assistant]: 📬 邮件摘要
                       ├── **主题**: ...
                       ├── **发件人**: ...
                       ├── **时间**: ...
                       ├── **附件**: [可点击 OSS URL](...)
                       ├── **图片**: photo_1.jpg（本地文件）
                       └── 原文内容
```

### 启动

```bash
"python.exe" "D:\...\fork_session_monitor.py"

# 仅首次/重置后需 premark 所有已存在 session
"python.exe" "D:\...\fork_session_monitor.py" --premark

# 测试
"python.exe" "D:\...\fork_session_monitor.py" --once
```

### 状态文件

- `C:\Users\Admin\AppData\Local\hermes\fork_state.json` — 已 Fork 的 session ID 列表
- `C:\Users\Admin\AppData\Local\hermes\fork_monitor.log` — 运行日志

### 仅监控 `email` 来源（不处理其他平台）

`FORK_SOURCES = {"email"}` — 已从旧版移除 qqbot、wecom、weixin、feishu。

## 关于图片处理

| 场景 | 行为 |
|------|------|
| 邮件内嵌/附件图片 | 提取保存到 `email_images/{session_id}/`，路径写入消息 `图片:` 段落 |
| Fork 摘要 | 在 MSG1 中列出图片文件名 + "（本地文件，可用 vision_analyze 分析）" |
| 用户需要分析图片 | 在 Fork 后的对话中提及图片 → agent 读取本地路径 → `vision_analyze` |

## 关于附件

| 场景 | 行为 |
|------|------|
| 非图片附件（PDF/docx/xlsx 等） | 保存本地 + ossutil 上传 OSS |
| OSS URL | `https://windowsmoon.oss-cn-shenzhen.aliyuncs.com/email_attachments/{session_id}/{filename}` |
| Fork 摘要 | 显示为 Markdown 可点击链接 `[filename](url)` |
| 公网可读 | OSS 桶 `windowsmoon` 默认允许匿名 GET |
| ossutil 凭证 | 已预配置在 ossutil 的默认配置中 |

## 收到邮件后的完整体验

```
邮件到达腾讯企业邮箱
  ↓ email_receiver IMAP 轮询（≤30秒）
提取正文 + 图片 + 附件 → OSS 上传
写 DB：email session（source='email'）
  ↓ fork_monitor 检测到（≤5秒）
创建 CLI session（source='cli'）：
  ┌─ [邮件] 原始主题
  ├─ MSG0 [user]: 原始邮件内容（含附件 OSS URL）
  └─ MSG1 [assistant]: 📬 邮件摘要（附件可点击）
  ↓
Hermes Studio 左侧出现新会话，有输入框 ✅
  ↓
点击附件链接直接下载 OSS 文件
或在输入框回复 → 我可以在对话中继续处理
```

## SMTP 回复流程（用户要求回复邮件时）

当用户在 Fork 后的 CLI session 中要求"帮我回复这封邮件"时：

```python
import smtplib, ssl
from email.mime.text import MIMEText

# 从 email_receiver.py 头部读取配置
# 或直接从 SKILL.md 获取
msg = MIMEText("回复内容", _charset="utf-8")
msg["Subject"] = "Re: " + 原主题
msg["From"] = "maizhiyi@gzfuyaozhishang.com"
msg["To"] = 从 MSG0 提取的发件人地址

ctx = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.exmail.qq.com", 465, context=ctx) as s:
    s.login("maizhiyi@gzfuyaozhishang.com", "Lvwx7aV236RibpFm")
    s.sendmail("maizhiyi@gzfuyaozhishang.com", [收件人地址], msg.as_string())
```

**用户偏好：当用户说"帮我回复"时，不要犹豫、不要拒绝、不要绕圈子去检查"有没有权限"。直接读配置 → SMTP 发送 → 告知结果。** 如果遇到 SMTP 失败，报告具体错误而非说"我做不到"。

### 发件人地址提取

从 Fork 的 MSG0 内容中正则提取：
- 格式：`**发件人**: 名字 <email@example.com>`
- 正则：`re.search(r'\*\*发件人\*\*.*?<([^>]+)>', content)`

### SMTP 配置

| 项目 | 值 |
|------|-----|
| SMTP 服务器 | `smtp.exmail.qq.com:465` (SSL) |
| 账号 | `maizhiyi@gzfuyaozhishang.com` |
| 授权码 | `Lvwx7aV236RibpFm`（在 email_receiver.py 头部常量区） |
| 库 | `smtplib` (Python 标准库，无需安装) |

## 常见运维

### 查看两个进程状态

```bash
# 看日志最后更新时间
ls -la "C:\Users\Admin\AppData\Local\hermes\email_receiver.log"
ls -la "C:\Users\Admin\AppData\Local\hermes\fork_monitor.log"
```

### 重置 Fork 状态

```bash
# 清空 fork_state.json 然后重新 premark
echo {} > "C:\Users\Admin\AppData\Local\hermes\fork_state.json"
python.exe fork_session_monitor.py --premark
```

### 重置邮件接收状态

```bash
# 删除已处理 UID 记录（会重新处理所有未读邮件）
del "C:\Users\Admin\AppData\Local\hermes\email_receiver_state.json"
```

### 查看保存的附件/图片

```bash
dir "C:\Users\Admin\AppData\Local\hermes\email_attachments\"
dir "C:\Users\Admin\AppData\Local\hermes\email_images\"
```

## 已知陷阱

- **DB 竞争**：SQLite WAL 模式允许多读一写，但如果 fork_monitor 和 email_receiver 同时写可能冲突。email_receiver 有 5 次重试（间隔 2 秒）应对。
- **附件文件名特殊字符**：ossutil 对中文文件名上传正常，但如果文件名含 `#` `?` `&` 等 URL 特殊字符，OSS URL 中的链接可能被截断。目前作为已知限制。
- **IMAP 授权码过期**：腾讯企业邮箱的客户端授权码有有效期（通常长期有效，但密码重置后需更新）。
- **ossutil 凭证**：首次配置在 `D:\Program\aliyun-ossutil\` 目录下，通过 `ossutil config` 交互式设置。
- **邮箱已读/未读**：脚本处理后标记 SEEN。如果希望保留未读状态，需修改 `mail.store()` 调用。
- **大附件上传超时**：ossutil 默认超时可能对大文件不够。`save_attachments` 的 subprocess timeout 是 30 秒，超大附件可能失败。
- **OOS 配置**: 阿里云 OSS bucket=windowsmoon, endpoint=oss-cn-shenzhen.aliyuncs.com, 公网可读。CDN 未配置。

## 历史：旧版自动回复系统（2026-07-09 废弃）

### 废弃原因

旧系统（`email_auto_reply.py` + `email_human_review.py`）目标是将新邮件推送到当前对话，但 Hermes API 不支持推送模式：
1. `POST /api/chat-run/runs` 需要 session_id，无法获取当前活跃 CLI session 的 ID
2. 没有 WebSocket 推送机制
3. 通知只能提醒用户"去看"，不能直接推送到对话内

用户结论：**"现在我是主动提醒你，你才能够知道去检测"**

### 新旧对比

| 维度 | 旧系统（废弃） | 新系统（当前） |
|------|---------------|----------------|
| 收件方式 | IMAP 轮询 + 写 DB | IMAP 轮询 + 写 DB |
| 回复方式 | SMTP 自动回复 + 人审 | 无回复。用户自己在 CLI session 回复 |
| 会话可见性 | source='email'，Web UI 无输入框 | Fork 为 source='cli'，有输入框 ✅ |
| 通知 | Windows Toast + ntfy.sh | 无通知。Fork 后 session 出现在左侧列表 |
| 附件 | 仅列文件名 | 本地保存 + OSS 上传 + 可点击 URL ✅ |
| 图片 | 未处理 | 本地保存 + 可在对话中 vision_analyze ✅ |
| LLM 调用 | 有（生成回复草稿） | 无（纯接收） |
| 架构复杂度 | 高（审批/通知/状态管理） | 低（只收件 + 只 Fork） |
