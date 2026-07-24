---
name: search-router
description: >
  当用户说"去网上搜一下"、"搜索一下"、"查查"等模糊搜索指令时使用。
  自动按四层分工路由：国内=open-webSearch+AnySearch+知乎、国际=Tavily+Exa、热点=TrendRadar、垂类=专业工具。
  不要用于：用户明确指定了用哪个工具（直接调对应工具）、不需要搜索的场景。
  触发词：搜索、查一下、搜一下、去网上搜、找找、帮我搜
tags:
  - search
  - router
  - websearch
  - chinese
  - zhihu
  - international
triggers:
  - 搜索
  - 查一下
  - 搜一下
  - 去网上搜
  - 找找
  - 帮我搜

---

# 搜索路由中心

## 核心分工（四层+知乎）

| 层次 | 工具 | 免费额度 | 适合场景 |
|:----:|------|:--------:|---------|
| 🏠 **国内搜索** | open-webSearch(百度) + AnySearch(结构化) | 无限+1,000次/天 | 通用中文搜索 |
| 📚 **知乎专搜** 🆕 | `zhihu-search` CLI（站内搜索+直答） | 5,000次/天 | 社区经验/问答/深度讨论 |
| 🌍 **国际搜索** | Tavily + Exa | 各~1,000次/月 | 英文/海外 |
| 🔥 **热点监控** | TrendRadar（8平台） | 无限 | 实时热点 |
| 🎯 **专业垂类** | SenseNova + xhs-cli + Tabbit | 不等 | 学术/代码/社媒 |

---

## 执行规则

### 知乎搜索（新增）— 何时自动使用

涉及以下场景时，**在常规搜索之外额外加调 zhihu-search**：
- 搜技术方案/工具评测（知乎有大量一线工程师实战分享）
- 搜行业趋势/市场分析（知乎有深度分析帖）
- 搜具体问题（"XX怎么实现""XX好不好用"）
- 需要对比多个方案时

**用法：** 同一轮搜索任务中，中文搜索 + 知乎搜索并行，两边结果融合输出。

```python
# 同一任务里并行调用
open-webSearch(百度, "RAG 评测方法")      # 通用网页
AnySearch("RAG 评测方法")                  # 结构化结果
zhihu-search search "RAG 评测方法" --scope zhihu --count 10  # 知乎社区
zhihu-search ask "RAG 评测的主流方法"       # 直答（知乎大模型总结）
```

### 路由规则完整表

| 你的指令 | 自动调用的工具 |
|---------|--------------|
| 🏠 **搜中文/搜国内** | `open-webSearch(百度)` + `AnySearch` + **`zhihu-search search`**（3路并行） |
| 🌍 **搜英文/国外** | `Tavily` + `Exa` |
| 🔥 **看热点/热搜** | `TrendRadar`（8平台） |
| 📚 **搜知乎/知乎搜** | `zhihu-search search --scope zhihu` + `zhihu-search ask` |
| 🧠 **直答/知乎AI答** | `zhihu-search ask --model thinking` |
| 🎓 **论文/学术** | `sensenova-sn-search-academic` |
| 💻 **代码/开源** | `sensenova-sn-search-code` |
| 📱 **小红书** | `xhs-cli` |
| 📊 **股价/公司** | `sensenova-sn-search-finance` + `sn-search-market-cn` |
| 🔬 **深度调研** | AnySearch + Tavily/Exa + zhihu-search + TrendRadar 组合 |

---

## 已配置工具清单

### 国内层
| 工具 | 方式 | 状态 |
|------|------|:----:|
| open-webSearch | MCP（百度/Bing等10引擎） | ✅ |
| AnySearch | REST API（1,000次/天） | ✅ |
| **zhihu-search** 🆕 | **CLI（搜知乎+直答，5,000次/天）** | **✅** |

### 国际层
| 工具 | 状态 |
|------|:----:|
| Tavily | ✅ |
| Exa | ✅ |

### 热点层
| 工具 | 状态 |
|------|:----:|
| TrendRadar | ✅ |

### 专业垂类
| 工具 | 状态 |
|------|:----:|
| SenseNova系列（8个） | ✅ |
| xhs-cli（小红书） | ✅ |
| Tabbit（反爬浏览器） | ✅ |

---

## ⚠️ 铁律

1. **搜中文 = 3路并行**（open-webSearch + AnySearch + zhihu-search），不要少任何一个
2. **知乎搜索上限10条/次**，需要更多可以换关键词搜多次合并
3. **直答(ask)比搜索更省Token** — 知乎大模型直接返回总结好的答案
4. **搜不到附搜索记录**
5. **每次新增搜索工具后立即更新搜索路由表**
