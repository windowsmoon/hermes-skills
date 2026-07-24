---
name: smart-video
description: >
  当用户需要智能视频剪辑时使用。
  3模式路由：简单混剪（剪映草稿）/全面混剪（pyJianYingDraft）/花费混剪（NemoVideo）。
  不要用于：AI生成视频（走hyperframes）、纯音频处理、图片转视频。
  触发词：混剪视频、智能剪辑、视频混剪、剪映、自动剪视频
tags:
  - video
  - editing
  - routing
  - capcut
  - jianying
  - nemovideo
  - chatcut
  - content-creation
triggers:
  - 混剪视频
  - 智能剪辑
  - 视频混剪
  - 剪映
  - 自动剪视频

---

# 智能视频剪辑生成器 — 3模式路由

## 触发方式

> "帮我把这些素材剪成一个视频"
> "帮我用这些素材做一个关于【主题】的视频"
> 用户在素材目录下说"帮我处理这些视频"

## 完整路由决策树

```
你说：帮我把这些视频素材处理成一条视频
  ↓
我先识别你的需求复杂度：
  ┌─────────────────────────────────────────────────────┐
  │ ① 🟢 简单混剪 — jianying-editor-skill              │
  │    自然语言驱动，快速出片，适合素材少、需求简单      │
  ├─────────────────────────────────────────────────────┤
  │ ② 🔵 全面混剪 — pyJianYingDraft ★推荐              │
  │    Python 完整控制，美颜/特效/转场/字幕全开（SVIP） │
  ├─────────────────────────────────────────────────────┤
  │ ③ 💰 花费混剪 — NemoVideo                           │
  │    云端AI一站式，免费额度有限，用完需付费            │
  └─────────────────────────────────────────────────────┘

  ↓
你选模式 → 我用对应工具处理
```

---

## 各模式详细说明

### ① 简单混剪 → jianying-editor-skill

**适合：** 素材少（2-3个），需求简单，快速出片

**流程：**
```
1. 你把素材放文件夹，说"帮我剪一下"
2. jianying-editor-skill 自动：
   ├─ 素材导入时间轴
   ├─ AI 配音（剪映音色 + 微软语音）
   ├─ 自动拆句+字幕对齐
   ├─ 特效/转场/滤镜（一句话应用）
   └─ 自动导出 MP4（需剪映 5.9 及以下）
3. 输出: 剪映草稿 + MP4
```

**依赖：** 剪映专业版 5.9 或更低 ✅ / Python 依赖已装 ✅
**限制：** ❌ 美颜/智能抠图不可用（需 GPU 实时渲染）；推荐 Windows + 剪映 5.9

---

### ② 全面混剪 → pyJianYingDraft ★ 推荐

**适合：** 素材多，需要完整控制，你是剪映 SVIP

**流程：**
```
1. 你把素材放文件夹，我分析内容
2. pyJianYingDraft 全套管线：
   ├─ 视频/音频/图片素材任意添加
   ├─ 剪映全部转场 + 特效 + 滤镜
   ├─ 剪映美颜（美白/磨皮/瘦脸/大眼）← SVIP 福利
   ├─ 剪映 TTS 配音（200+ 音色）
   ├─ 智能字幕 + 花字/气泡/关键帧/蒙版
   └─ 生成草稿 → 你在剪映打开→手动导出（或自动导出需5.9版）
3. 输出: 剪映草稿（.draft 文件）
```

**依赖：** `pip install pyJianYingDraft` ✅ / 剪映 SVIP ✅
**注意：** 新版剪映（v7+）草稿可能加密，自动导出不可用，需手动打开剪映导出。点几下鼠标的事，相比省下的 $100/月非常值得。

---

### ③ 花费混剪 → NemoVideo

**适合：** 愿意付费，需要云端一站式处理

**流程：**
```
1. 你把素材上传到 NemoVideo
2. 自然语言驱动机器：
   ├─ SmartPick 自动选片（删除无效镜头）
   ├─ 对话式转场："加个炫酷转场"
   ├─ 电影滤镜（TrendyPop / RitmoFun）
   ├─ TTS 男/女声 + 自动配 BGM
   └─ 弹跳字幕动画 → 导出
3. 输出: MP4 下载链接
```

**接入方式：** OpenClaw Skill（`clawhub install nemo-video`）或直接调 REST API
**限制：** 免费 100 额度，用完需付费

---

## 路由优先级

| 你的场景 | 推荐模式 | 工具 |
|---------|---------|------|
| 素材少、需求简单 | ① 简单混剪 | jianying-editor-skill |
| 全面控制、美颜全开 | ② 全面混剪 | pyJianYingDraft |
| 愿意付费、省事 | ③ 花费混剪 | NemoVideo |
| 在线剪辑、对话式 | ① 简单混剪 | jianying-editor-skill |
| 最高质量、SVIP 福利 | ② 全面混剪 | pyJianYingDraft |

## 交互规范

当用户触发视频剪辑任务时，**必须**先问用户想用哪种模式，呈现为编号选择题：

```
> 你想怎么剪？
  1. 🟢 简单混剪 — 自然语言驱动，快速出片（jianying-editor-skill）
  2. 🔵 全面混剪 — 完整控制，美颜/特效全开，你已是SVIP（pyJianYingDraft）
  3. 💰 花费混剪 — 云端AI一站式，免费额度有限（NemoVideo）
  0. 你帮我选
```

## 依赖检查

| 工具 | 状态 | 备注 |
|------|------|------|
| jianying-editor-skill | ✅ Hermes skills 目录 | git clone 完成 |
| pyJianYingDraft | ✅ pip install | 0.3.0 |
| NemoVideo | ⚠️ 需用户注册 | 需 API Key |
| 剪映专业版 | ✅ 用户已安装 | SVIP |

## 参考文件

- jianying-editor-skill: `~/AppData/Local/hermes/skills/jianying-editor-skill/SKILL.md`
- pyJianYingDraft 文档: `pip show pyJianYingDraft`
- video-use 参考: `~/AppData/Local/hermes/skills/video-use/SKILL.md`
- 视频工具对比矩阵: `D:/hermes-data/video-tool-matrix.html`
- 交互规范: `~/AppData/Local/hermes/skills/smart-ppt/references/interaction-pattern.md`