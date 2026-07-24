# 企业级 Hermes 底座架构详细设计

> 基于 D:\hermes-data\enterprise\ 的实际部署结构

## 目录结构

```
D:\hermes-data\enterprise\          ← 企业底座根目录（17 个文件）
├── ENTERPRISE_README.md            ← 架构总览
├── ROADMAP.md                      ← 三阶段实施路线图
│
├── GLOBAL\                          ← 共享底座（9 个模板文件）
│   ├── GLOBAL_CONTEXT.md            ← 全局上下文/规则
│   ├── SKILL_DEPENDENCIES.md        ← 技能依赖清单
│   ├── DEPARTMENTS.md               ← 部门注册表
│   ├── TOKEN_MANAGEMENT.md          ← Token 预算与用量
│   ├── LARK_PROFILES.md             ← 飞书多账号路由
│   ├── GITHUB_ACCOUNTS.md           ← GitHub 多账号
│   ├── OBSIDIAN_LINK.md             ← 知识库连接
│   ├── KNOWLEDGE_BASES.md           ← 多知识库索引
│   ├── PROJECTS.md                  ← 项目注册中心
│   └── .agents\skills\README.md     ← 全局 Skill 源头
│
├── DEPARTMENTS\                      ← 部门隔离层（3 个预设部门）
│   ├── operations\README.md         ← 运营部（预算 500 万/月）
│   ├── engineering\README.md        ← 研发部（预算 500 万/月）
│   └── hr\README.md                 ← 人事部（预算 100 万/月）
│
└── SCRIPTS\                          ← 管理脚本
    ├── init_department.py            ← 创建新部门（无 yaml 依赖）
    └── token_usage_report.py         ← 用量统计（带进度条）
```

## 创建日期

2026-07-22，本会话中创建。

## 快速启动

```powershell
cd D:\hermes-data\enterprise

# 查看部门状态
python SCRIPTS\token_usage_report.py

# 创建新部门
python SCRIPTS\init_department.py --name 运营部 --manager 张三 --monthly-budget 5000000

# 列出所有部门
python SCRIPTS\init_department.py --list

# 查看单个部门状态
python SCRIPTS\init_department.py --name 运营部 --status
```

## 部门 token.yaml 格式

```yaml
department: 运营部
manager: 张三
monthly_budget: 5000000
alert_threshold: 0.8
reset_day: 1
current_usage: 0
last_reset: 2026-07-01
```

## 告警规则

| 条件 | 动作 |
|------|------|
| 用量达到预算 80% | 飞书通知部门主管 |
| 用量达到预算 100% | 自动暂停非关键任务 |
| 用量超预算 120% | 暂停所有任务，需管理员恢复 |

## 关系图

详见 SKILL.md 中的架构图。

## 前置依赖

- Hermes Agent（已安装）
- Python 3.x（无需额外依赖，脚本纯标准库）