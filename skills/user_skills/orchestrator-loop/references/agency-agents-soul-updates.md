# agency-agents-zh SOUL 增强记录

## 来源
[jnMetaCode/agency-agents-zh](https://github.com/jnMetaCode/agency-agents-zh) — 266个AI角色配置，含50个中国原创角色

### 安装
```bash
git clone https://github.com/jnMetaCode/agency-agents-zh
cd agency-agents-zh
./scripts/convert.sh --tool hermes   # 转成 Hermes 格式
./scripts/install.sh --tool hermes   # 安装到 ~/.hermes/skills/
```
Hermes 格式安装后以 SKILL.md 形式存在，可直接使用。

## 已增强的 Profile（2026-07-18 初版 / 2026-07-21 补充）

| Profile | 模型 | 来源角色 | 新增核心内容 |
|:--------|:----|:--------|:------------|
| product-manager | deepseek-v4-pro | 产品经理 | 8条关键规则(先找问题不跳到方案/先写新闻稿再写PRD/会说不保护专注力/构建前验证上线后度量/对齐不等于同意/范围蔓延是杀手) + PRD交付物要求(问题陈述+成功指标表+Non-Goals+验收标准) |
| engineering-director | qwen3.7-plus | 后端架构师 | 6条关键规则(安全优先/水平扩展Day1设计/API版本控制+文档/软删除+审计字段标配/缓存一致性/事件驱动三种情况处理) + 交付物要求(架构模式说明+Schema+API规范+安全措施+性能预估) |
| qa-director | glm-5.2 | 现实检验者 | 5条关键规则(默认状态需要改进/首次C+/B-正常/生产就绪需要卓越表现/每项声明需要证据/5个自动不通过条件) + 交付物要求(现实检查证据+规格与实现对比+用户旅程测试+性能指标) |
| operations-director | minimax-m3 | 增长黑客 + 抖音策略师 | 增长纪律5条(无数据不做/每个实验明确假设/一次改一个变量/不欺骗式增长/CAC<LTV) + 抖音算法权重排序(完播率>点赞率>评论率>转发率) + 前3秒法则 + 直播结构(20%引流+50%利润+15%形象+15%福利) |
| bigdata-director | deepseek-v4-pro | 数据工程师 | 5条管线可靠性标准(幂等/schema契约/Null必须刻意/Gold层质量分数/软删除+审计字段) + Medallion原则(Bronze原始不可变→Silver清洗去重→Gold业务就绪) |

## 增强方式
直接写入每个 profile 的 `SOUL.md` 文件，保留原有身份定义，在下方新增 `## 核心能力`、`## 关键规则`、`## 交付物要求` 章节。未修改 default profile 的 SOUL.md。

## 参考角色 SOUL 原始文件
`C:/Users/Admin/AppData/Local/hermes/cache/agency-agents-zh/`

## 待建 profile 候选（285个角色可用）
完整清单见 `C:/Users/Admin/AppData/Local/hermes/cache/agency-agents-zh/` 各子目录。
已在 skills_list 中搜索：用户已列出全部角色但尚未新建 profile。
