# 国内 AI PPT 工具集成调研

## 有 API/SDK/MCP/Skill 的工具

| 工具 | 集成方式 | 详情 |
|-----|---------|------|
| **讯飞智文**（讯飞星火） | ✅ **MCP Server** | `aippt-mcp`，6 个工具：模板列表/创建PPT/查进度/创建大纲/文档转大纲/按大纲生成，需 APP_ID + API_SECRET |
| **Gamma.app** | ✅ **MCP** + **Python SDK** + **Skill** | MCP: `pip install gamma-app-mcp`，SDK: `gamma_ai_python_sdk_ppt_generator`，Skill: `gamma-ppt-skill`，需 Gamma Pro 套餐 + API Key |
| **文多多 AiPPT**（docmee.cn） | ✅ **REST API** + **SDK** | `docmee.cn/open-platform`，Python/Java/Go Demo，支持主题生成/文件转PPT/Word转PPT，免费接入 |
| **GordenPPTSkill** | ✅ **Hermes Skill** + **CLI** | SKILL.md 原生 + `build_pptx.py`，21 套中文模板，完全离线，免费开源 |
| **ChatPPT CLI**（@yooai/cli） | ✅ **CLI** | 79 个模板，支持字体/图片风格/页数定制，需登录（免费额度用完后需充值） |

## 无公开 API 的工具

| 工具 | 原因 |
|-----|------|
| **AiPPT.cn** | 纯网页端，无 API |
| **ChatPPT**（网页版） | 无公开接口 |
| **WPS AI** | 内置于 WPS |
| **iSlide** | 插件工具，无 API |
| **Beautiful.ai** | 海外付费工具，无公开 API |

## 各工具对比

| 维度 | **GordenPPTSkill** | **文多多 AiPPT** | **ChatPPT CLI** | **Gamma MCP** | **讯飞智文 MCP** |
|-----|-------------------|-----------------|----------------|--------------|----------------|
| 费用 | **免费开源** | 免费接入 | 免费额度（用完需充值） | Pro 套餐起 | 免费（讯飞星火） |
| 离线可用 | ✅ **完全离线** | ❌ 需联网 | ❌ 需联网 | ❌ 需联网 | ❌ 需联网 |
| 模板 | 21 套中文模板 | 文多多模板库 | 79 个模板 | Gamma 模板库 | 讯飞模板库 |
| AI 生成 | ❌ 依赖你的 LLM | ✅ 文多多 AI | ✅ ChatPPT AI | ✅ Gamma AI | ✅ 讯飞 AI |
| AI 配图 | ❌ 无 | ✅ 有 | ✅ 有 | ✅ Flux/Imagen/DALL-E | ✅ 自动/高级配图 |
| 集成方式 | Hermes Skill | REST API | CLI 命令 | MCP 协议 | MCP 协议 |
| 适用场景 | 离线/内网/免费 | 需要自动生成 | 精致定制 | 已有 Gamma 会员 | 免费中文 |
| 安装复杂度 | 低（pip install） | 中（需 API Key） | 中（需登录） | 中（需付费 API Key） | 中（需 APP_ID） |

## 当前集成状态

| 工具 | 状态 | 备注 |
|------|------|------|
| GordenPPTSkill | ✅ 已安装 | 21 套模板，离线可用 |
| 文多多 AiPPT | ✅ 已安装 | API Key 已配 |
| ChatPPT CLI | ✅ 已安装 | 免费额度已用完 |
| Gamma MCP | ❌ 未安装 | 需 Pro 套餐 |
| 讯飞智文 MCP | ❌ 未安装 | 需 APP_ID |