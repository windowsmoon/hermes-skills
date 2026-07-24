---
name: video-montage-router
description: >
  当用户需要路由到不同的大码女装视频混剪工具时使用。
  根据用户选择的混剪模式，自动路由到对应的管线（pyJianYingDraft/NemoVideo等）。
  不要用于：直接执行混剪（走video-montage-pipeline）、非穿搭类视频。
  触发词：视频混剪路由、选混剪模式、女装视频用哪个工具
tags:
  - video
  - montage
  - capcut
  - jianying
  - routing
  - plus-size-fashion
related_skills:
  - jianying-editor-skill
  - pyJianYingDraft
  - nemovideo-skills
trigger_phrases:
  - 混剪
  - 剪视频
  - 视频剪辑
  - 做视频
  - 大码女装
  - 穿搭视频
  - 素材
triggers:
  - 视频混剪路由
  - 选混剪模式
  - 女装视频用哪个工具

---

# 视频混剪路由 Skill

## 触发条件

当用户说要做视频、混剪、剪辑视频、处理素材时，触发本 Skill。

## 工作流程

### Phase 1: 识别用户意图

用户说出需求后，先判断是哪种视频制作需求：

| 关键词 | 模式 |
|:-------|:-----|
| 简单、快速、随便剪、试试 | **简单混剪** |
| 全面、精细、好好剪、美颜、特效、完整 | **全面混剪** |
| 花费、付费、Nemo | **花费混剪** |

如果用户没有明确说模式，**必须问用户选哪个**。

### Phase 2: 询问模式

```
问：你要用什么方式混剪？

① 简单混剪 — 快速出片，一句话驱动剪映，自动配音+字幕+转场
                工具：jianying-editor-skill（自然语言驱动剪映）
                适合：快速试效果、日常更新

② 全面混剪 — 精细控制剪映，美颜/特效/滤镜/关键帧全开
                工具：pyJianYingDraft（Python 直接操控剪映草稿）
                适合：出精品视频、需要精细调参

③ 花费混剪 — NemoVideo AI 云端剪辑（暂未配置，需付费套餐）
                工具：NemoVideo（OpenClaw Skill）
                适合：需要额外 AI 能力时
```

### Phase 3: 路由到对应工具

#### 简单混剪 → jianying-editor-skill

规则：
1. 用户把素材丢进一个文件夹
2. 告诉用户：把素材路径告诉我，我剪映自动出片
3. 调用 jianying-editor-skill 的规则和 prompts 生成剪映草稿
   - 参考 skill 目录: `~/AppData/Local/hermes/skills/jianying-editor-skill/`
   - 规则文件: `rules/` 目录
   - 提示词: `prompts/` 目录
4. 生成的草稿保存在剪映草稿目录 `.../JianyingPro Drafts/`
5. 用户打开剪映 → 找到草稿 → 手动调整 → 导出（SVIP 美颜/特效全可用）

**注意：** jianying-editor-skill 的美颜/智能抠图不能直接调用（需要剪映 GPU 实时渲染），但用户可以在剪映里手动加。

#### 全面混剪 → pyJianYingDraft

规则：
1. 用户把素材丢进一个文件夹
2. 用 pyJianYingDraft 生成完整的剪映草稿 JSON
3. 支持的功能：
   - 视频/音频/图片素材添加
   - 转场效果
   - 滤镜/特效
   - 文本/字幕/花字/气泡
   - 关键帧/蒙版/色度抠图
   - TTS 配音（剪映原生音色）
4. 生成的草稿保存在剪映草稿目录
5. 用户打开剪映 → 找到草稿 → 手动导出（或自动导出如果剪映 5.9）

#### 花费混剪 → NemoVideo

规则：
1. 告诉用户：NemoVideo 需要付费套餐才能使用 API Key
2. 如果用户愿意付费升级，提供 NemoVideo 官网链接
3. 等用户配置好 API Key 后再使用

## 素材路径约定

用户把素材放在一个文件夹，例如：
```
D:\videos\项目名\
├── clip1.mp4
├── clip2.mp4
├── clip3.mp4
└── ...
```

## 输出约定

| 模式 | 产出 | 位置 |
|:-----|:-----|:-----|
| 简单混剪 | 剪映草稿 + 可手动导出 | `.../JianyingPro Drafts/项目名/` |
| 全面混剪 | 剪映草稿 + 可选自动导出 | `.../JianyingPro Drafts/项目名/` |
| 花费混剪 | NemoVideo 云端渲染 | NemoVideo 云端 |

## 注意事项

- 剪映草稿目录通常在: `C:\Users\<用户名>\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft\`
- 新版剪映草稿可能加密，pyJianYingDraft 支持 fallback_loader
- 自动导出仅支持剪映 5.9 及以下版本
- 手动导出也很简单：打开剪映 → 找到草稿 → 导出 → 选分辨率