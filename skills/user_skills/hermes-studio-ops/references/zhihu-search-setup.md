# Zhihu Search（知乎搜索）设置指南

## 来源
- **知乎开放平台**: https://developer.zhihu.com/
- **zhihu-search MCP**: https://pypi.org/project/zhihu-search/ (v1.3.0, 2026-07-01)
- **作者**: Klarkxy

## 功能
知乎官方 API 的 CLI + MCP + OpenAPI + Skill 封装，4个接口：

| 接口 | CLI 命令 | 说明 |
|------|---------|------|
| 🔍 知乎搜索 | `zhihu-search search "关键词" --scope zhihu` | 站内搜问答/文章/用户，上限10条 |
| 🌐 全网搜索 | `zhihu-search search "关键词" --scope web` | 全网搜索，上限20条，支持 filter |
| 🤖 直答 | `zhihu-search ask "问题"` | 知乎自研大模型（fast/thinking/agent 三档） |
| 🔥 热榜 | `zhihu-search trending --limit 30` | 当前知乎热榜 |

## 安装
```bash
pip install zhihu-search
```

## 配置
1. 在 https://developer.zhihu.com/ 注册账号
2. 登录后创建应用，获取 Access Secret
3. 保存凭证：
```bash
zhihu-search --save-token "zh-your-secret-here"
```

## MCP 模式
```bash
zhihu-search serve
```

MCP 客户端配置：
```json
{
  "mcpServers": {
    "zhihu-search": {
      "command": "zhihu-search",
      "args": ["serve"]
    }
  }
}
```

暴露 3 个工具：`search`、`ask`、`trending`。

## 免费额度
- **5,000 次/天**（知乎开放平台免费层）
- 熔断保护：连续 2 次限流 → 熔断 6 小时
- 查看状态：`zhihu-search --quota`

## 在 Hermes 中的定位
作为 **中文 UGC/社区搜索** 补充：
- 秘塔搜索 → 学术/论文
- 知乎搜索 → 真实经验/社区讨论
- open-webSearch → 通用网页
- 三者互补，覆盖中文搜索的不同维度

## 搜索参数
```bash
# 知乎站内搜索（问答+文章+用户）
zhihu-search search "RAG 评测" --scope zhihu --count 5 --format json

# 全网搜索
zhihu-search search "AI 2026" --scope web --count 10

# 热榜
zhihu-search trending --limit 10

# 直答（知乎大模型）
zhihu-search ask "什么是 MCP 协议？" --model thinking
```

## 注意事项
- `--scope zhihu` 上限 10 条，`--scope web` 上限 20 条
- Access Secret 是敏感凭证，不要写进聊天记录或截图
- 凭证按优先级读取：`ZHIHU_ACCESS_SECRET` 环境变量 > `~/.config/zhihu-search/credentials.json`
