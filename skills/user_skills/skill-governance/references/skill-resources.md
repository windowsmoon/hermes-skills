# Skill 资源站与搜索阶梯

## 技能资源站

| 网站 | 说明 | 搜索方式 | 链接 |
|------|------|---------|------|
| **skills.sh** | 全球最大 Agent Skills 市场（Vercel），94万+技能，支持 Hermes/OpenCode/Codex/Claude Code | `hermes skills search` / `npx skills find` / 浏览器搜索 | https://www.skills.sh/ |
| **clawhub.ai/skills** | OpenClaw 官方 Skill 站 | 浏览器搜索 | https://clawhub.ai/skills |
| **skillhub.club** | 中文 Skill 排行榜，聚合 skills.sh 数据 | 浏览器搜索 | https://skillhub.club/hot |
| **xiaping.coze.com** | 虾评，Coze 官方社区，2248个技能，有评测评分 | 浏览器搜索 + `coze plugin install` | https://xiaping.coze.com/ |
| **modelscope.cn/skills** | 阿里魔搭社区 Skills 中心，7.6万+技能 | 浏览器搜索 | https://modelscope.cn/skills |
| **skillsmp.com** | 技能市场（中文） | 浏览器搜索（需Cloudflare验证） | https://skillsmp.com/zh |
| **腾讯 SkillHub** | 腾讯官方 AI Skills 社区，兼容 Hermes/Claude Code/Codex 等主流 Agent，已验证技能 | 浏览器搜索 | https://skillhub.cloud.tencent.com |

## 搜索阶梯（优先顺序）

### 完整 5 层搜索协议（2026-07-20 定稿）

```
本地没有现成skill
  │
  第1层（<1秒）：查本地已安装
  │   hermes skills list + 注册中心MD
  │
  第2层（<5秒）：find-skills 工具
  │   npx skills find <关键词> → 搜 skills.sh（94万+）
  │
  第3层（<5秒）：Hermes CLI 搜索
  │   hermes skills search <关键词>
  │
  第4层（<30秒）：各技能资源站（浏览器）
  │   ① modelscope.cn（阿里魔搭，中文优先）
  │   ② xiaping.coze.com（虾评，Coze生态）
  │   ③ clawhub.ai（OpenClaw生态）
  │   ④ skillhub.club（中文聚合排行）
  ⑤ 腾讯 SkillHub（腾讯官方，已验证技能）
  │
  第5层（<60秒）：广义网络搜索
  │   web_search "API for X" / "CLI for X" / "MCP server for X"
  │
  都找不到 → 确认无结果，附搜索记录
```

### 搜索工具选择

| 搜索方式 | 适用场景 | 工具 |
|---------|--------|------|
| **skill名称搜索** | 知道大概叫什么名 | `hermes skills search <名称>` |
| **关键词搜索** | 不知道叫什么，只知道要什么能力 | `npx skills find <关键词>` |
| **浏览器搜索** | 前两者都搜不到，需要去特定网站 | 浏览器导航到各资源站 |
| **API搜索** | 网站有公开API时 | 暂无可用的公开API，都是Web页面 |

**优先使用 skill搜索/关键词搜索（第2-3层）**，因为 skills.sh 市场已经覆盖94万+技能，绝大多数需求在这里能找到。

### 各资源站的技术能力评估

| 网站 | 有CLI/API？ | 有搜索工具？ | 评估 |
|------|-----------|------------|------|
| **skills.sh** | ✅ `npx skills find` + `hermes skills search` | ✅ find-skills（2.6M安装量） | 最佳选择，94万+技能 |
| **modelscope.cn** | ❌ 无公开API | ❌ 仅浏览器搜索 | 阿里云官方，中文友好 |
| **xiaping.coze.com** | ❌ 无公开API | ❌ 仅浏览器搜索 | Coze生态，有评分 |
| **clawhub.ai** | ❌ 无公开API | ❌ 仅浏览器搜索 | OpenClaw生态 |
| **skillhub.club** | ❌ 无公开API | ❌ 仅浏览器搜索 | 聚合排行 |
| **腾讯 SkillHub** | ❌ 无公开API | ❌ 仅浏览器搜索 | 腾讯官方，兼容Hermes |
| **skillsmp.com** | ❌ 无公开API | ❌ 仅浏览器搜索 | 需Cloudflare验证 |

**结论：只有 skills.sh 有 CLI 搜索工具。** 其他网站只能浏览器搜索。所以搜索顺序中，skills.sh 的 CLI 搜索是最高效的，其他网站作为兜底补充。

### prefill_messages_file 配置（提升 skill 调用率）

2026-07-20 配置了 prefill_messages_file，在每次对话开始时注入 5 条铁律到系统提示词顶部，确保关键指令不会被长上下文冲淡。

配置文件：`~/.hermes/prefill.json`

```json
[
  {"role": "system", "content": "【铁律1】每次新增 skill/CLI/MCP/API/插件到任何 Profile 后，必须立即更新 Profile能力矩阵.md"},
  {"role": "system", "content": "【铁律2】执行复杂任务前，先读 Profile能力矩阵.md，判断哪个 Profile 有合适工具"},
  {"role": "system", "content": "【铁律3】找工具时：先翻 Hermes 已有生态 → 搜至少3个方向 → 搜不到才说没有，附上搜索记录"},
  {"role": "system", "content": "【铁律4】用户只跟 default Profile 说话，零感知中间过程，只有出错才报用户"},
  {"role": "system", "content": "【铁律5】任务来了先走8步流程：①感知→②拆解→③读能力矩阵→④决策→⑤找工具→⑥执行→⑦汇总→⑧更新"}
]
```

### 常见问题：Hermes 能否为其他 Agent 安装 skill？

| 目标 Agent | 能否通过 Hermes 安装？ | 方式 |
|-----------|---------------------|------|
| **OpenCode** | ✅ 能 | `npx skills add` 通过 Hermes 的 terminal 执行 |
| **Coze** | ⚠️ 部分能 | Coze 有自己的插件市场，但 `coze plugin install` 可通过 CLI 执行 |
| **Claude Code** | ✅ 能 | 通过 `npx skills add` 安装到 Claude Code 的 skills 目录 |
| **Codex** | ✅ 能 | 通过 `npx skills add` 安装到 Codex 的 skills 目录 |

**本质：** Hermes 可以通过 terminal 工具执行任何 CLI 命令，所以理论上能为任何有 CLI 的 Agent 安装 skill。

## 用户指定 Skill 名称但找不到时的处理流程

当用户说"安装一个叫 XXX 的 skill"但精确匹配不到时：

```
用户说"安装 XXX skill"
  │
  ├── ① 本地已安装？ → 有则直接使用
  │
  ├── ② 精确搜索：搜 "XXX" → 没找到
  │
  ├── ③ 根词搜索：搜根词（如 "true-damand" → "demand" / "true"）
  │
  ├── ④ 找到相似项？
  │   ├── 有 → 列出最接近的 alternatives（带安装量/来源）
  │   └── 无 → 说明没找到，附搜索记录
  │
  └── ⑤ 问用户
      ├── 是不是拼写错了？
      ├── 是不是指某个相近的 skill？
      └── 要不要创建一个自定义 skill？
```

**关键原则：** 搜不到不要搜一次就说没有。至少搜：
- 精确名称
- 根词/部分匹配（skills.sh + ClawHub 两个市场）
- 如果用户没回应，把搜索记录和相近 alternatives 列出来

## 搜索关键词规则

`[能力领域] + [动作]`

| 想要的 | 关键词 |
|--------|--------|
| 生成PPT | `ppt generation` |
| 写测试用例 | `test case writing` |
| 数据分析 | `data analysis excel` |
| 抖音视频 | `douyin video pipeline` |
| API接口 | `api design` |
| 前端组件 | `react component` |
| 代码审查 | `code review` |
| 部署 | `deployment` |

先用英文搜（skills.sh 以英文为主），搜不到换中文（modelscope/虾评以中文为主）。

## 安装命令速查

| 目标 | 命令 |
|------|------|
| Hermes | `hermes skills install <标识符>` |
| OpenCode | `npx skills add <GitHub包名>` |
| Coze | `coze plugin install <插件名>` |
| Claude Code | `npx skills add <包名>` |
| Codex | `npx skills add <包名>` |

## 踩坑记录

### 1. Windows 下 npx skills find 乱码

在 Windows git-bash/MSYS 终端中，`npx skills find` 的输出可能包含乱码/二进制数据，exit_code=1 但实际可能成功。原因：终端编码问题。

**解决：** 优先使用浏览器搜索 `https://www.skills.sh/search?q=<关键词>`，比 CLI 更可靠。

### 2. 搜索结果不精确

skills.sh 的搜索对部分匹配不友好（如搜 "true-damand" 找不到，但搜 "demand" 能找到相关项）。先用根词搜索，再人工筛选。

### 3. 浏览器搜索 vs CLI 搜索

skills.sh 浏览器搜索能看到完整结果（名称、来源、安装量），CLI 搜索只返回名称列表。浏览器搜索更便于判断质量。

## find-skills 工具

- 来源：`vercel-labs/skills`（2.6M 安装量，skills.sh 排行第1）
- 安装：`hermes skills install skills-sh/vercel-labs/skills/find-skills`
- 用途：搜索技能市场，找到合适的 skill 后安装
- 触发：当用户说"帮我找能做 XXX 的 skill"时
- 注意：该 skill 是 hub-installed（受保护），不可编辑。补充知识（如本文件中的坑）应放在 skill-governance 的 references 中。