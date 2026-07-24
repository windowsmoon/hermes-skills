# 企业级 Skill 治理扩展

> 从单机 skill 治理到跨部门企业级 skill 治理的演进。
> 详细的企业级部署方案见 `enterprise-agent-deployment` skill。

## 单机 vs 企业级 Skill 治理

| 维度 | 单机治理（skill-governance） | 企业级治理（enterprise-agent-deployment） |
|------|---------------------------|---------------------------------------|
| Skill 范围 | 当前 Profile 的 skill | 跨部门、全局+部门两级 |
| 安装位置 | 当前 Hermes 安装目录 | GLOBAL/.agents/skills/ + DEPARTMENTS/{部门}/skills/ |
| 权限 | 管理员可写 | 全局只读，部门可写本部门 |
| 注册中心 | Obsidian MD 本地文件 | GLOBAL/DEPARTMENTS.md + 各部门 README |
| 依赖清单 | 无（手工管理） | SKILL_DEPENDENCIES.md 统一清单 |
| Token 管理 | 无 | 部门预算制 + 用量告警 |

## 企业级 Skill 分类

| 级别 | 位置 | 谁可见 | 谁可写 | 例子 |
|------|------|--------|--------|------|
| 全局 Skill | GLOBAL/.agents/skills/ | 所有部门 | 管理员 | init-agent-project, feishu-profile |
| 部门 Skill | DEPARTMENTS/{部门}/skills/ | 仅本部门 | 部门主管 | social-media-scraper(运营部) |
| 外部 Skill | 通过 SKILL_DEPENDENCIES.md 记录 | 按需安装 | 用户 | find-skills, open-webSearch |

## 部门 Skill 升级流程

1. 部门验证 Skill 质量达标（至少运行 10 次无报错）
2. 部门主管提出升级申请
3. 管理员审批通过
4. 移入 GLOBAL/.agents/skills/ 并更新 SKILL_DEPENDENCIES.md
5. 通知所有部门更新

## 跟 skill-governance 三条原则的关系

企业级治理是对三条原则的扩展应用：

| 原则 | 单机应用 | 企业级扩展 |
|------|---------|---------|
| 入口治理 | description 写边界 | 加上"部门可见性"边界 |
| 手册治理 | skill 写成地图 | 加上"跨部门共享说明" |
| 错误治理 | 纠错沉淀回 skill | 加上"部门级反馈回全局"