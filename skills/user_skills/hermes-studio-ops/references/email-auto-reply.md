# Email Auto-Reply Support

## 脚本位置
`D:\hermes-data\email_auto_reply.py`

## 腾讯企业邮箱配置（已填写）
```python
CONFIG = {
    "email_addr":  "maizhiyi@gzfuyaozhishang.com",
    "email_user":  "maizhiyi@gzfuyaozhishang.com",
    "email_pass":  "Lvwx7aV236RibpFm",
    "imap_host":   "imap.exmail.qq.com",
    "imap_port":   993,
    "smtp_host":   "smtp.exmail.qq.com",
    "smtp_port":   465,
    "smtp_user":   "maizhiyi@gzfuyaozhishang.com",
    "smtp_pass":   "Lvwx7aV236RibpFm",
}
```

## 验证命令
```bash
# 完整功能测试
"C:\Users\Admin\.hermes-web-ui\desktop-runtime\hermes\0.18.0\win-x64\python\python.exe" "D:\hermes-data\email_auto_reply.py" --test-full

# 查看状态
"C:\Users\Admin\.hermes-web-ui\desktop-runtime\hermes\0.18.0\win-x64\python\python.exe" "D:\hermes-data\email_auto_reply.py" --status
```

## Task Scheduler 任务
- 任务名：`HermesEmailAutoReply`
- 状态：`schtasks /Query /TN HermesEmailAutoReply /FO LIST`

## 日志
`D:\hermes-data\email_auto_reply.log`

## 关键架构
- 脚本写 `hermes-web-ui.db`（source='email'）而非通过 Hermes Web API
- session 直接出现在 Hermes Studio UI 左侧会话列表
- 用户在 Hermes 回复 → 脚本轮询 DB → SMTP 发回
- 无需任何 API token 或外部依赖