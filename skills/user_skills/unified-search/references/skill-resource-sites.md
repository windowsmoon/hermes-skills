# Skill 资源站 — 搜索 Agent Skill 的市场

> 当用户需要找现成的 Agent Skill 时，先搜技能市场，再不自己造轮子。

## 技能市场网站

| 网站 | 说明 | 技能数 | 链接 |
|------|------|--------|------|
| **skills.sh** | 全球最大 Agent Skills 市场（Vercel 出品），支持 Hermes/Nous Research、OpenCode、Codex、Claude Code 等所有主流 Agent | 94万+ | https://www.skills.sh/ |
| **skillhub.club** | 中文 Skill 排行榜，聚合 skills.sh 数据 | — | https://skillhub.club/hot |
| **xiaping.coze.com** | 虾评 Skill，Coze 官方社区，有评测评分和下载量 | 2248 | https://xiaping.coze.com/ |
| **clawhub.ai/skills** | OpenClaw 官方 Skill 站，分类浏览 | — | https://clawhub.ai/skills |
| **modelscope.cn/skills** | 阿里魔搭社区 Skills 中心，阿里云官方出品，含支付宝、DataWorks 等企业级 Skill | 7.6万+ | https://modelscope.cn/skills |
| **skillsmp.com** | 技能市场（中文，需 Cloudflare 验证） | — | https://skillsmp.com/zh |

## 各 Agent 官方 Skill 来源

| Agent | 官方来源 | 获取方式 |
|-------|---------|---------|
| **Claude Code** | `anthropics/skills`（GitHub） | skills.sh 筛选 `?agent=claude-code` |
| **Codex** | skills.sh 生态 | skills.sh 筛选 `?agent=codex` |
| **OpenCode** | skills.sh 生态 | skills.sh 筛选 `?agent=opencode` |
| **Hermes (Nous Research)** | skills.sh 生态 | skills.sh 筛选 `?agent=nous-research` |

## 通过 Hermes CLI 搜索技能

```bash
# 搜索技能市场
hermes skills search <关键词>

# 预览技能不安装
hermes skills inspect <标识符>

# 安装技能
hermes skills install <标识符>

# 浏览所有可用技能
hermes skills browse
```

## find-skills 工具（已安装）

- 来源：`vercel-labs/skills`（2.6M 安装量，skills.sh 排行第1）
- 安装标识符：`skills-sh/vercel-labs/skills/find-skills`
- 底层调用：`npx skills find [关键词]`
- 用途：当用户说"帮我找能做 XXX 的 skill"时触发

## 搜索策略

当用户在 unified-search 中搜索工具/技能时，增加以下搜索步骤：

1. 先 + 已有的搜索源（Tavily/Exa/秘塔等）
2. 再 + `hermes skills search <关键词>`
3. 再 + 手动浏览 skills.sh 等网站
4. 汇总结果给用户