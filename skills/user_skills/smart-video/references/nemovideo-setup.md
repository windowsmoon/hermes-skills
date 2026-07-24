# NemoVideo 接入指南

## 概述
NemoVideo 是一个云端 AI 视频编辑服务，前 TikTok 团队创立，~$10M 融资。
支持通过 OpenClaw Skill 或直接 REST API 调用。

## 安装方式

### 方式 A：OpenClaw Skill（推荐）
```bash
npm install -g clawhub
clawhub install nemo-video
```

### 方式 B：直接 REST API
API 端点：`https://mega-api-prod.nemovideo.ai`
需要先在 https://www.nemovideo.com 注册账号获取 API Key。

## 免费额度
- 首次注册：100 免费积分（匿名自动生成，7天过期）
- 用完后需充值

## 支持的功能
- SmartPick 自动选片（删除无效/枯燥镜头）
- 对话式转场
- 电影滤镜（TrendyPop / RitmoFun / ArteMoment）
- TTS 男/女声 + 自动配 BGM
- 弹跳字幕动画
- 多平台导出（TikTok/YouTube/Reels/Shorts）

## 注意
- 所有处理在云端完成，需要网络
- 免费额度有限，用完需付费
- 目前 OpenClaw 方式安装可能失败（依赖 GitHub 可访问性）