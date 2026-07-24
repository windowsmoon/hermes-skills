---
name: unified-search
description: >
  当用户需要搜索信息，且不确定用什么搜索工具、或需要同时覆盖网络和本地笔记时使用。
  自动路由到最佳搜索源（Tavily/Exa/秘塔/Firecrawl/Obsidian/open-webSearch），支持并行搜索+去重+排序。
  不要用于：仅搜索本地笔记（走Obsidian RAG）、仅搜索单一网站（走浏览器）、深度分析（走sn-deep-research）。
  触发词：帮我搜一下、查一下、搜索、找资料、research
tags: [search, obsidian, rag, tavily, exa]
triggers:
  - 搜一下
  - 查一下
  - 搜索
  - 帮我搜
  - research
  - 查资料
  - 找一下关于
---

# Unified Search：统一搜索

## 核心场景

自媒体/内容创作者调研新工具、新模型、新方法时，需要**一次搜索同时覆盖**：
- 🌐 网络（最新 AI 工具、模型发布、AIGC 方法）
- 📁 本地笔记（个人 Obsidian 知识库，历史记录）
- 🧠 历史对话（之前讨论过的相关内容）

传统做法：浏览器搜一遍 → Obsidian 搜一遍 → 翻聊天记录 → 手动整合
这个 skill：一句话，全搜完。

## 触发词

用户说类似：

> "帮我搜一下 2026 年最新的 AI 视频生成工具"
> "查资料：Sora 最新进展"
> "research 一下开源图像放大模型"
> "帮我找找关于 ComfyUI 工作流优化的东西"

## 核心规则：呈现格式（用户严格要求，必须遵守）

### 规则 0：显示全部结果，不自行过滤
用户要 N 条就给 N 条。不要根据关键词/内容做预过滤。分类标记（加标签/分组）可以在输出层做，但不要删除任何结果。用户自己判断相关性。

### 规则 1：每条结果必须有 URL
不要只给标题不给链接。每条结果必须包含：**标题 + 摘要快照 + 完整可点击 URL**。🔗 符号引导 URL。

### 规则 2：每条结果必须有内容预览
从原文抓取前 200-400 字作为快照。如果抓取失败，注明原因（反爬/超时/403），**不要留空**。

### 规则 3：必须解释来源状态
如果某个搜索源返回 0 条结果，必须说明原因，不要只写"无结果"：
- ✅ "Tavily: 返回了 N 条带摘要的结果"
- ⚠️ "Exa: 返回了论文标题但正文为空（API 免费版限制），可用 web_extract 补抓"
- ⚪ "Obsidian: 本地笔记未命中该关键词"

### 规则 4：推荐排序
标记哪些结果最值得优先阅读，用 🔥 / 📖 / 📎 三级。

### 规则 5：对比搜索工具时，必须逐项枚举搜索源
不得用"等"、"多个引擎"、"各种来源"等模糊表述。必须列出每个工具的**具体搜索引擎清单**，分类展开。中文友好度是必备对比维度。

### 全局搜索范围控制 `--scope`
默认 **article**。用户可改 news / web / academic：
| --scope | 秘塔 scope | Exa category | 场景 |
|---------|-----------|-------------|------|
| article（默认） | web | article | 文章优先 |
| news | news | news | 新闻动态 |
| web | web | web | 全网兜底 |
| academic | academic | research paper | 学术论文 |

## 当前的搜索源
| 源 | 类型 | 状态 | 覆盖 |
|----|------|------|------|
| 🌐 **open-webSearch** | MCP Server（免 API Key） | ✅ 已装+已注册 | Bing/百度/CSDN/搜狗/掘金/DuckDuckGo/Brave/Startpage/Exa（共10个引擎） |
| 🌐 **Tavily** | API（有 Key） | ✅ 已配 | 通用网络搜索 |
| 🌐 **Exa** | API（有 Key） | ✅ 已配 | 语义搜索（article/news/research paper） |
| 🌐 **秘塔 AI** | API（有 Key） | ✅ 已配 | 中文全网搜索 |
| 🌐 **SenseNova搜索**（10个） | Hermes Skill | ✅ 已装 | 学术/代码/金融/社交/市场/年报等 |
| 🌐 **bailian-cli** | Python脚本 | ✅ 已装 | 阿里云搜索 |
| 🛒 **Apify MCP** | MCP Server（需API Token） | ✅ 已装 | 淘宝/天猫/京东/1688/抖音/闲鱼电商数据采集（见 references/apify-chinese-ecommerce.md） |
| 🔍 **xhs-cli** | CLI | ✅ 已装+已登录 | 小红书 |
| 📊 **TrendRadar** | Hermes Skill | ✅ 已装 | 微博/知乎/抖音/B站/头条等热点 |
| 📁 **Obsidian RAG** | 本地向量库 | ✅ 已配 | 本地笔记 |
| 🔄 **AnySearch** | REST API（已配 Key） | ✅ 已装+已配置 | 22个垂直领域，1,000次/天免费 |
| 🐳 **SearXNG** | Docker自部署（待装） | ⏳ 可装 | 248个引擎全覆盖 |

## 工作流程

### Phase 1：解析查询

1. 用户给出搜索意图和关键词
2. 拆解为多个子查询（如需要）

### Phase 2：并行搜索

使用 `scripts/unified_search.py` 脚本统一搜索（默认 max=10，Tavily 免费版上限 10）：

```python
scripts/unified_search.py "<查询词>" --sources all --max 10
```

脚本同时调用：
- Tavily API（AI 摘要）— 免费版单次最多 10 条
- Exa API（语义搜索）— 支持 category 参数 + contents.text 获取正文
- Firecrawl API（网页抓取）— **v0 API 非 v1**
- 秘塔 API（中文搜索）— 支持 `page` 翻页，可自动遍历多页凑够数量（最多70条）
- **open-webSearch MCP** — 免 API Key，Bing/百度/CSDN/搜狗/掘金等多引擎
- Obsidian RAG（本地笔记查询）

同时 Agent 还会并行执行：
- `session_search()` 搜索历史对话
- Hindsight 自动检索长期记忆（已配置 auto_recall=true）

### 秘塔翻页机制（关键）

秘塔 API 每页最多返回 10 条，但支持 `page` 参数翻页。脚本自动遍历多页直到凑够用户请求的数量：

| 用户请求 | 实际翻页 | API 调用次数 |
|---------|---------|:-----------:|
| `--max 10` | page=1 | 1 次 |
| `--max 20` | page=1,2 | 2 次 |
| `--max 50` | page=1~5 | 5 次 |
| `--max 70` | page=1~7 | 7 次（安全上限） |

翻页不消耗额外 credits（实测多次调用 credits 不递减）。

### 秘塔搜索范围

通过环境变量 `MITA_SCOPE` 控制：

```bash
MITA_SCOPE=academic python scripts/unified_search.py "扩散模型" --sources mita --max 20
```

或通过 Agent 传参：在查询中说明方向即可，如"搜 xxx，学术方向"。

| 值 | 范围 |
|----|------|
| `web` | 网页（默认） |
| `academic` | 学术论文 |
| `news` | 新闻 |
| `wiki` | 百科 |
| `video` | 视频（可能无索引） |

### 全局搜索范围优先级

通过 `--scope` 参数控制所有工具的统一搜索方向，默认 **article**：

| 参数 | 秘塔 scope | Exa category | 适用场景 |
|------|-----------|-------------|---------|
| `--scope article`（默认） | web | article | 文章类，日常调研首选 |
| `--scope news` | news | news | 最新动态、行业资讯 |
| `--scope web` | web | web | 全网搜索，兜底 |
| `--scope academic` | academic | research paper | 学术论文、技术报告 |

优先级顺序：article → news → web → academic。用户指定后自动映射到各工具的参数。

### open-webSearch 引擎切换

通过环境变量控制引擎：`OWS_ENGINE=baidu` / `OWS_ENGINE=bing`。在查询中说明即可。参考 `references/open-websearch.md`。

### Exa category 与正文获取

Exa 支持 `category` 参数和 `contents.text`：

```python
# 获取学术论文 + 正文摘要
{
    "query": "...",
    "category": "research paper",  # news, article, company, pdf
    "contents": {"text": True}     # 关键！返回正文而非仅标题
}
```

注意：免费版 Exa 仍然经常只返回标题不返回正文。脚本已在 `search_exa()` 中启用 `contents.text`，但如果返回为空，需额外用 `web_extract` 抓取。详见 `references/exa-content-enrichment.md`。

### 可选来源筛选

| 参数 | 搜索范围 |
|------|---------|
| `--sources all` | Tavily + Exa + Firecrawl + 秘塔 + Obsidian |
| `--sources web` | 仅网络（Tavily + Exa + Firecrawl + 秘塔） |
| `--sources obsidian` | 仅本地 Obsidian |
| `--sources tavily` | 仅 Tavily |

### Phase 3：合并与排序

1. 去重（URL 去重 + 内容相似去重）
2. 按相关性排序（网络最新优先，本地笔记权威优先）
3. 标记每条结果的来源（🌐 网络 / 📁 笔记 / 🧠 记忆）

### Phase 3.5：摘要快照（关键步骤）

对 Tavily / Exa / Firecrawl 返回的前 N 条结果，用 `web_extract` 或直接 HTTP 抓取文章正文，提取纯文本摘要（前 200-400 字），作为**快照预览**附在结果中。

这样用户不需要点开每个链接就能判断：

```
📖 19款工具深度对比
📝 2026年AI视频生成工具盘点发布，字节Seedance 2.0、LibTV等19款工具深度对比...
🔗 https://...（完整URL）
```

### Phase 4：呈现（严格遵循以下规则）

#### 规则 1：每条结果必须包含 URL
不要只给标题，不给链接。每条结果 === `标题 + 快照摘要 + 完整可点击URL`。

#### 规则 2：每条结果必须有内容预览
从原文抓取前 200-400 字作为快照。如果抓取失败，注明原因（反爬/超时），不要留白。

#### 规则 3：解释来源状态
如果某个搜索源返回 0 条结果，必须说明原因，不要只写"无结果"：
- "Tavily: API 返回正常但该查询无匹配结果"
- "Exa: 返回了论文标题但正文为空（API 限制）"
- "Firecrawl: v0 API 不含标题/URL 字段，需从 content 解析"
- "Obsidian: 本地笔记未命中该关键词"

#### 规则 4：推荐排序
标记哪些结果最值得优先阅读：

```
🔥 最推荐先看 — [文章标题]（理由：覆盖面最广/最新/最相关）
📖 其次 — ...
📎 参考 — ...
```

#### 输出格式示例

```
═══ 统一搜索结果：「xxx」 ═══

🔥 推荐优先阅读
━━━━━━━━━━━━━━━━━━━━━━━━━
① 文章标题
📝 文章摘要预览（200-400字）
🔗 https://完整可点击URL

② 文章标题
📝 摘要预览...
🔗 https://...

📚 补充参考
━━━━━━━━━━━━━━━━━━━━━━━━━
③ ...

📁 本地笔记
━━━━━━━━━━━━━━━━━━━━━━━━━
（未命中 / 命中的笔记列表）

🧠 历史讨论
━━━━━━━━━━━━━━━━━━━━━━━━━
（相关历史会话）

📊 来源状态
━━━━━━━━━━━━━━━━━━━━━━━━━
• Tavily: ✅ N条（免费额度剩余约XXX/1000）
• Exa: ✅ N条
• Firecrawl: ⚠️ N条（说明限制）
• Obsidian: ⚪ 未命中
```

## 已配置的搜索源

所有搜索 API Key 已配置（~/.hermes/.env 内），skill 自动使用：

1. ✅ **Tavily** — tvly-dev-xxx（1,000 次/月）
2. ✅ **Exa** — 67cc607e-xxx（语义搜索）
3. ✅ **Firecrawl** — fc-b2fe46xxx（网页抓取）
4. ✅ **Obsidian RAG** — 本地 FAISS 向量库

## 脚本路径

统一搜索脚本位于 `scripts/unified_search.py`，支持 CLI 直接调用：

```
python scripts/unified_search.py "查询词" --sources all --max 10
```

各来源可单独调用：`--sources tavily`、`--sources exa`、`--sources firecrawl`、`--sources obsidian`。

## 降级策略

如果某个 API 调用失败（额度用完/网络问题），自动降级到下一个可用源：
- Tavily 失败 → 降级到 Exa / Firecrawl
- 全部网络搜索失败 → 降级到 `web_search`（Hermes 内置）
- 至少保证有搜索结果返回

## 参考资料

详见 `references/search-api-quirks.md` — 各 API 的端点、参数、限额、常见坑点（Firecrawl v0/v1 差异、Exa content 为空等）。

## 参考资料索引

| 文件 | 内容 |
|------|------|
| `references/search-source-matrix.md` | **搜索源完整矩阵** — 所有已知搜索工具的引擎覆盖、部署方式、中文友好度、选择决策树 |
| `references/search-sources-config.md` | 各搜索源的具体配置参数 |
| `references/open-websearch.md` | open-webSearch MCP 安装与引擎切换（Bing/Baidu/Sogou等） |
| `references/search-registry.md` | 搜索源注册表 |
| `references/search-api-quirks.md` | 各API的端点、参数、限额、常见坑点 |
| `references/exa-content-enrichment.md` | Exa 正文获取 |
| `references/metaso-api.md` | 秘塔 API 调用 |
| `references/paseo-research-20260718.md` | Paseo Agent 编排平台调研 |
| `references/apify-chinese-ecommerce.md` | **Apify 中国电商平台数据覆盖** — 淘宝/天猫90+字段详解、京东/1688/抖音/闲鱼/微店覆盖情况、Actor列表、MCP Server安装与坑点 |
| `references/skill-resource-sites.md` | Agent Skill 资源站 — skills.sh 等技能市场，`hermes skills search` 命令，find-skills 工具 |
| `references/gemini-vision.md` 🆕 | **Gemini 3.5 Flash 视觉理解** — vision API 调用方式、已验证能力、配置信息 |

## 进阶：模型定价调研

当用户需要对比中国 AI 模型（豆包/Qwen/DeepSeek 等）的**定价和规格**时，参考 `references/chinese-cloud-pricing-research.md`：

- 各云平台官方定价页 URL
- 火山引擎动态页面的提取技术（browser_console + JS）
- 阿里云百炼 SPA 页面的数据提取
- 第三方定价聚合站
- 价格单位换算速查（元/千token ↔ 元/百万token）
- 常见失败场景与降级策略
