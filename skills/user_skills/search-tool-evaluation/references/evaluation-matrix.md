# 搜索工具评估矩阵

## 对比表（2026-07-22）

| 工具 | 类型 | 免费额度 | 中文能力 | 独特价值 | 结论 |
|:----:|:----:|:--------:|:--------:|:--------:|:----:|
| open-webSearch | 多引擎聚合 | 无限 | ✅ 百度/Bing | 10引擎+免Key | ✅ 在用 |
| AnySearch | 自建索引 | 1,000次/天 | ✅ 结构化 | 22垂直领域 | ✅ 在用 |
| zhihu-search | 深搜+直答 | 5,000次/天 | ✅ 知乎全站 | 直答=知乎大模型总结 | ✅ 在用 |
| Tavily | AI搜索 | 1,000次/月 | ❌ | AI摘要 | ✅ 在用 |
| Exa | 语义搜索 | 有免费层 | ❌ | 语义匹配 | ✅ 在用 |
| TrendRadar | 热点监控 | 无限 | ✅ 8平台 | 实时聚合 | ✅ 在用 |
| xhs-cli | 平台客户端 | 无限 | ✅ 小红书 | 完整操作 | ✅ 在用 |
| **AgentKey** | **聚合网关** | **付费** | **✅ 多平台** | **微博/微信/B站/抖音** | **❌ 不装** |
| **Codex Skill Universe** | **本地UI** | **免费** | **❌** | **Skill管理** | **❌ 不装** |

## 详细评估

### AgentKey（https://console.agentkey.app）

**覆盖：** Tavily + Serper + Brave + Perplexity + 微博 + 微信 + 小红书 + B站 + 知乎 + 抖音

**问题：**
1. **网页搜索**：AnySearch 自建索引+22垂类 > AgentKey 通用搜索
2. **知乎**：zhihu-search 直答=知乎大模型总结 > AgentKey 只是抓数据
3. **小红书**：xhs-cli 完整客户端（搜索/浏览/点赞/评论）> AgentKey 数据接口
4. **缺失部分**（微博/B站/抖音/微信）：open-webSearch(百度) + AnySearch 基本能覆盖
5. **付费**：Cloudflare Worker 托管，需要订阅

**唯一值得考虑的场景：** 精确搜索某个微博帖子/B站视频/抖音内容（不是看热点，是找具体内容）。但这种情况不多，真遇到了用 open-webSearch 也能覆盖。

### Codex Skill Universe（https://github.com/kangyize/codex-skill-universe）

**本质：** 本地 Web UI（Node.js + Vite），不是 API/MCP

**功能：**
- 3D 可视化 Skill 生态图
- 推荐雷达（从 ClawHub 推荐新 Skill）
- AI Skill Doctor（分析 Skill 质量，需配 OpenAI Key）
- Skill Groups（工作流）
- Research Mission Mode（研究项目管理）

**问题：**
- 不能直接被 Agent 调用（没有 API/MCP 端点）
- 只是给人类用的管理工具
- 对 Agent 的实际搜索能力无帮助

### zhihu-search（https://github.com/klarkxy/zhihu-search）

**独特价值：**
- **直答（ask）**：知乎自研大模型直接总结，比搜索更省 Token
- **深度**：知乎全站内容（问题/回答/文章/用户），远超通用搜索引擎
- **免费**：5,000次/天，够日常使用

**互补关系：**
| 秘塔搜索 | 知乎搜索 |
|:--------:|:--------:|
| 学术/论文/深度 | 社区讨论/真实经验/问答 |
| 结构化、权威 | 活人回答、实战经验 |
| ❌ 直答 | ✅ 知乎大模型直接总结 |
