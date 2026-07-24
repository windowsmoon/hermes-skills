# HeartFlow 实测结果记录

## 结论：心虫不适合做用户心理学分析

### 测试数据
- Session: mrda3w8jd4s8cy（1136条消息，7天深度技术对话）
- 调用工具：heartflow_think, heartflow_emotion, heartflow_persona_stance_detector, heartflow_agent_psychology

### 各工具实测表现

| 工具 | 输入 | 输出 | 评价 |
|------|------|------|------|
| heartflow_think | 247字用户行为描述 | 模板化判断："general类型，calculation领域，severity low" | 浅层分类，缺乏深度 |
| heartflow_emotion | 真实用户对话摘录 | type=unknown, intensity=0 | 对真实文本无效 |
| heartflow_persona_stance_detector | 用户行为描述 | 返回引擎内部场域数值(U/D/A/H) | 不是用户立场分析 |
| heartflow_agent_psychology | 会话上下文 | 7维引擎认知状态（healthScore=1, focus=deep_focus） | 分析的是引擎自己 |

### 正确的使用方式
- 用 heartflow_status 检查服务健康
- 用 heartflow_agent_psychology 了解引擎自身状态
- 用我自己的分析能力代替心虫做深度用户分析（基于记忆中的User Profile）
