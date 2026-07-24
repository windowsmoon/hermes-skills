# AI PPT 工具集成调研结果（2026-07-17）

## 有公开 API / MCP / SDK 的工具

### 1. Gamma.app
- **MCP**: `pip install gamma-app-mcp` (PyPI)
- **SDK**: `gamma_ai_python_sdk_ppt_generator` (GitHub, TechWithTy)
- **Skill**: `gamma-ppt-skill` (ClawHub, evaouyang-ai)
- **API**: Gamma Public API v1.0 (developers.gamma.app)
- **要求**: Gamma Pro/Ultra/Teams/Business 套餐

### 2. 讯飞智文（iFlyTek）
- **MCP**: `iguangyu/aippt-mcp` ⭐8 — 6 个 MCP 工具
  - get_theme_list / create_ppt_task / get_task_progress / create_outline / create_outline_by_doc / create_ppt_by_outline
- **要求**: 讯飞 AIPPT_APP_ID + AIPPT_API_SECRET

### 3. 文多多 AiPPT（docmee.cn）
- **REST API**: `https://docmee.cn/api/` — 文档: docmee.cn/open-platform
- **SDK**: Python/Java/Go Demo (docmee/aippt-api-*-demo on GitHub)
- **API Key**: 通过开放平台获取
- **API 流程**: apiKey → createApiToken(2h有效) → generateOutline → generateContent → randomTemplate → generatePptx → download
- **免费额度**: 有免费试用额度

### 4. GordenPPTSkill
- **Hermes Skill**: SKILL.md 原生支持
- **CLI**: `scripts/build_pptx.py`
- **离线本地生成**, 21 套中文模板
- **仓库**: github.com/GordenSun/GordenPPTSkill

## 无公开 API 的工具
- AiPPT.cn（网页端）
- ChatPPT（无 API）
- WPS AI（内置 WPS）
- iSlide（插件）
- Beautiful.ai（海外）

## 安装方式总览
```
Gamma MCP:       pip install gamma-app-mcp
讯飞 MCP:        git clone + MCP server 注册
文多多 API:      POST https://docmee.cn/api/ + Api-Key
GordenPPT:       git clone + python-pptx + SKILL.md 注册
```
