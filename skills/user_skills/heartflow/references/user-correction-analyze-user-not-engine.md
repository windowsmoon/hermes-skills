# 用户纠正：心虫分析的是用户本人，不是 AI 引擎

## 事件（2026-07-17）

用户说：`心虫评估：对session：mrda3w8jd4s8cy 分析我的认知水平`

我调用了 HeartFlow 的 `heartflow_agent_psychology` 和 `heartflow_think` 工具，但返回的是引擎自身的 7 维认知状态（认知负荷、注意力焦点、经验沉淀等），而不是对用户的认知分析。

用户纠正：`我是让你叫心虫分析我本人，不是你分析你`

## 教训

1. HeartFlow 的 31 个 MCP 工具，绝大多数是分析 **AI 引擎自身状态** 的，不是分析用户的工具
2. `heartflow_think` 对输入文本做浅层意图分类（return template-like responses）
3. `heartflow_emotion` 对真实用户文本返回 `type=unknown`
4. `heartflow_agent_psychology` 返回引擎的 7 维认知心理状态
5. 没有哪个心虫工具能做真正的用户心理学分析

## 正确做法

如果用户要求分析"我本人"的认知水平/性格，应该：
1. 基于 User Profile（之前保存的详细性格画像）做分析
2. 基于对话历史和用户行为模式自己分析
3. 心虫只做辅助验证，不依赖它做主要分析
