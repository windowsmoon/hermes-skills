---
name: user-preferences-media-search
description: 用户关于媒体生成（图片/视频）和搜索工具的偏好与配置记录。
  所有配置通过对话完成，不让用户改文件。
tags: [preferences, media, search, image, video]
---

# 用户偏好：媒体生成 & 搜索（2026-07-18 建立）

## 配置原则
- 所有配置通过对话完成，不让用户改文件
- 飞书 Webhook URL、平台启用/关闭、关键词都通过对话交流

## 图片生成
- 主力: **豹剪 gpt-image-2-4k** (api.bjzy.nfai.top) — 稳定可用，无安全拦截
- 历史保留: 心流 grop/gpt-image-2 — 安全策略拦截图片生成，仅保留用于视频
- FAL_KEY 已设系统环境变量，重启 Hermes 后 image_generate 工具可用

## 视频生成
- 模型: **sora-v4-fast** (iliu.ai)
- API: 提交 POST /v1/videos/generations → 轮询 GET /v1/videos/{task_id}
- 支持尺寸: 960x960, 1280x720, 720x1280, 1920x1080, 1080x1920, 1080x1080
- 异步任务，需轮询等待完成

## 搜索 API 注意事项
- 榜眼数据（get-the-news）正确参数是 `q`，不是 `keyword`
- 秘塔搜索参数是 `q`，scope 支持 web/news/academic/wiki/video
- Exa 支持 category 参数: research paper, news, article, company, pdf
- unified-search --scope 默认 article，优先级 article→news→web→academic

## 飞书文档写入
- 用 tenant_access_token 创建，不要用 lark-cli
- tenant_access_token 不支持 block_type 3/4/5（标题块）
- 用 block_type=2 加粗文本模拟标题
- 不要用 MD 表格语法写飞书（飞书不渲染 MD 表格）
