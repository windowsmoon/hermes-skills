# 技能资源站搜索工具审计

> 2026-07-21 审计结果。记录各技能资源站是否有可被Agent直接调用的CLI/API/MCP搜索工具。

## 审计结论

**只有 skills.sh 有可被Agent直接调用的CLI搜索工具。** 其他网站都只能通过浏览器手动搜索。

## 详细审计表

| 网站 | 技能数 | 有无CLI/API搜索工具 | 搜索方式 | 备注 |
|------|--------|-------------------|---------|------|
| **skills.sh** | 94万+ | ✅ **有** | `npx skills find <关键词>` 或 `hermes skills search <关键词>` | Vercel出品，全球最大Agent Skills市场。支持按Agent筛选（Hermes/OpenCode/Codex/Claude Code）。 |
| **xiaping.coze.com**（虾评） | 2251 | ❌ 无公开API/CLI | 仅Web搜索框+分类筛选 | Coze官方社区，有评分和评测。域名已迁移至coze.com。 |
| **clawhub.ai/skills**（OpenClaw） | 大量 | ❌ 无公开API/CLI | 仅Web搜索框+分类筛选 | OpenClaw生态，支持GitHub登录。有Audit功能。 |
| **modelscope.cn/skills**（阿里魔搭） | 7.6万+ | ❌ 无公开API/CLI | 仅Web搜索框 | 阿里云官方，有MCP广场但搜索"共0个"。阿里云SDK存在但不支持skill搜索。 |
| **skillhub.club**（聚合排行） | 聚合 | ❌ 无公开API/CLI | 仅Web页面 | 聚合skills.sh数据的中文排行榜。 |
| **skillsmp.com** | — | ❌ 无公开API/CLI | 需Cloudflare验证 | 中文技能市场，但被Cloudflare保护，无法直接访问。 |

## 搜索优先级

```
本地没有现成skill
  │
  ① 本地已安装（hermes skills list + 注册中心MD）
  ② find-skills CLI（npx skills find <关键词>，搜skills.sh）
  ③ hermes CLI（hermes skills search <关键词>，也搜skills.sh）
  ④ 各技能资源站（浏览器搜索，按以上顺序）
  ⑤ 广义网络搜索（web_search "API/CLI/MCP for X"）
  ⑥ 都找不到 → 确认无结果，附搜索记录
```

## 搜索关键词规则

```
关键词格式：[能力领域] + [动作]
先用英文搜（skills.sh以英文为主），搜不到换中文（modelscope/虾评以中文为主）
先宽后窄（先搜大类，搜不到再缩小）
```

## 踩坑记录

### Windows 下 npx skills find 乱码

在Windows git-bash/MSYS终端中，`npx skills find` 的输出可能包含乱码/二进制数据，exit_code=1但实际可能成功。

**解决：** 优先使用 `hermes skills search`（走Hermes bundled Python，编码正常），或在浏览器中搜索skills.sh。

### skills.sh 支持 Hermes

skills.sh 的Agent筛选列表中包含 **Nous Research（Hermes）** 和 **OpenCode**，说明Hermes生态被skills.sh官方支持。