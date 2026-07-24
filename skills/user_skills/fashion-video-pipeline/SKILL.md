---
name: fashion-video-pipeline
description: >
  当用户需要fashion-video-pipeline时使用。
  不要用于：无关场景。
  触发词：穿搭视频、服装视频、大码女装、做穿搭视频
tags:
  - video
  - fashion
  - clothing
  - beautification
  - tts
  - montage
  - plus-size
  - content-creation
related_skills:
  - video-use
  - bailian-cli
  - remotion
  - hyperframes
prerequisites:
  commands: [ffmpeg, ffprobe]
  skills: [video-use, bailian-cli]
triggers:
  - 穿搭视频
  - 服装视频
  - 大码女装
  - 做穿搭视频

---

# Fashion Video Pipeline — 穿搭视频制作管线

## 触发条件

当用户要求从**素材库**中挑选视频片段，制作**穿搭/服装/大码女装主题**视频时，使用本技能。

典型触发句：
- "帮我从这些视频素材里挑几个片段，剪成一个穿搭视频"
- "我想做一个大码女装显瘦穿搭的视频，素材都在这个文件夹里"
- "帮我把这些素材拼成一个有主题的服装展示视频"
- "从素材库选片，做一个微胖女生穿搭指南"

## 核心概念

本技能区别于 `video-use` 的核心差异：

| 维度 | video-use | fashion-video-pipeline |
|:-----|:----------|:----------------------|
| 素材来源 | 用户已指定用哪些素材 | 从**素材库**中**自动挑选**合适的片段 |
| 叙事结构 | 跟随原素材的叙事 | 按**主题卖点**重新编排（开场→痛点→解决方案→展示→对比→结尾） |
| 美颜 | 只做调色（grade） | 额外做**皮肤磨皮+美颜**（smartblur） |
| 旁白 | 无（用原声） | **TTS生成旁白**覆盖原声 |
| 适用场景 | 口播/录屏/教程 | 服装展示/穿搭/产品种草 |

## 管线架构

```
┌──────────────────────────────────────────────────┐
│ 你的素材库（N个视频片段）                         │
└──────────────────────┬───────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────┐
│ STEP 1: 素材分析 + 智能选片                      │
│  → 提取关键帧 + vision分析内容                    │
│  → 读取每个片段元数据（时长/分辨率）              │
│  → LLM 选出最佳组合片段                           │
└──────────────────────┬───────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────┐
│ STEP 2: 剧本编排 + 旁白文案                      │
│  → 设计故事线（HOOK→痛点→解决方案→展示→CTA）     │
│  → 为每个片段写旁白文案（大码女装卖点）            │
│  → 生成时间轴（每个片段时长分配）                  │
└──────────────────────┬───────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────┐
│ STEP 3: 美颜美化 + 调色（per-segment）            │
│  → smartblur 皮肤磨皮                             │
│  → vibrance 服装颜色增强                          │
│  → colorbalance 肤色校正                          │
│  → unsharp 整体锐化                               │
│  详见 references/fashion-beautification-pipeline.md│
└──────────────────────┬───────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────┐
│ STEP 4: TTS 旁白配音                              │
│  → 用 bailian-cli tts (CosyVoice) 或 Edge-TTS    │
│  → 选择适合女装调性的音色                         │
│  → 按时间轴生成多段音频文件                        │
└──────────────────────┬───────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────┐
│ STEP 5: 视频拼接 + 转场                          │
│  → ffmpeg xfade 57种转场（fade/slide/dissolve等） │
│  → 片段间 30ms 音频淡入淡出防爆音                 │
│  → 背景音乐混音（可选）                           │
└──────────────────────┬───────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────┐
│ STEP 6: 字幕生成 + 烧录                          │
│  → 旁白文案 → SRT 字幕文件                       │
│  → ffmpeg subtitles filter 烧录到视频             │
│  → 字幕样式：中文字体+大号+高对比度               │
└──────────────────────┬───────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────┐
│ STEP 7: 包装成片                                  │
│  → 片头/片尾（image_generate 生成封面图）          │
│  → 品牌Logo/水印叠加                              │
│  → 统一输出为最终视频                             │
└──────────────────────────────────────────────────┘
                       ↓
              最终成片（带旁白+字幕+美颜+转场）
```

## 详细步骤

### Step 1: 素材分析 + 智能选片

**目标：** 从素材库中自动选出能组成一个完整主题的片段。

**方法：**

```
1. 遍历素材目录，ffprobe 获取每个片段的元数据
2. 对每个片段，提取 3-5 个关键帧（开头、中间、结尾）
3. 用 vision_analyze 分析每个关键帧：
   - 画面内容（人物/服装/场景/动作）
   - 服装类型（连衣裙/上衣/裤子/外套等）
   - 拍摄角度（全身/半身/特写）
   - 背景/场景（室内/室外/试衣间/街拍）
4. 用 bailian-cli asr 或 video-use 的 Scribe 转录对话（如果有原声）
5. LLM 综合分析，选出最佳片段组合
```

**选片原则（大码女装）：**
- 必须有正面/侧面/背面的服装展示
- 优先选光线好、颜色正的片段
- 覆盖不同角度（全身→半身→细节特写）
- 如果有"穿搭前后对比"片段，优先保留

**CLI 关键帧提取：**
```bash
# 从视频中提取关键帧（场景变化检测）
ffmpeg -i input.mp4 -filter:v "select='gt(scene,0.4)',showinfo" -vsync vfr -frames:v 5 keyframes/%03d.jpg 2>/dev/null
```

### Step 2: 剧本编排 + 旁白文案

**大码女装标准叙事结构：**

```
HOOK（3-5秒）        → "微胖女生看过来！这件裙子真的太显瘦了！"
PAIN POINT（5-8秒）  → "很多姐妹觉得微胖不好买衣服，怕显胖..."
SOLUTION（5-8秒）    → "今天给大家推荐几款真正遮肉显瘦的单品"
SHOWCASE（15-20秒）  → 多角度展示服装上身效果
BEFORE/AFTER（5-8秒）→ 穿搭前后对比/搭配技巧
DETAIL（5-8秒）      → 面料/版型/设计细节特写
CTA（3-5秒）         → "喜欢的话点个关注，下次继续分享"
```

**旁白文案要点：**
- 每段文案控制在 15-25 字/秒（正常语速）
- 卖点关键词：显瘦、遮肉、修饰腿型、显高、气质、舒适、百搭
- 避免负面词汇，用正面引导（"遮肉"→"修饰曲线"）
- 每段文案需标注时间戳，与片段对齐

### Step 3: 美颜美化 + 调色

**标准美颜管线（按顺序）：**

```bash
# 皮肤磨皮（保留边缘，只模糊皮肤区域）
ffmpeg -i input.mp4 -vf "smartblur=lr=2.0:ls=0.5:lt=10:cr=1.0:cs=0.5:ct=20" \
  -c:a copy output_smooth.mp4

# 服装颜色增强（提升饱和度，不过度）
ffmpeg -i output_smooth.mp4 -vf "vibrance=ib=0.2:ig=0.1:ir=-0.1" \
  -c:a copy output_vibrant.mp4

# 肤色校正 + 整体调色
ffmpeg -i output_vibrant.mp4 -vf "colorbalance=rs=0.05:gs=0.02:bs=-0.03" \
  -c:a copy output_color.mp4

# 锐化（提清晰度）
ffmpeg -i output_color.mp4 -vf "unsharp=5:5:0.8:3:3:0.4" \
  -c:a copy output_sharp.mp4
```

**等价合并命令（一次编码）：**
```bash
ffmpeg -i input.mp4 -vf \
  "smartblur=lr=2.0:ls=0.5:lt=10:cr=1.0:cs=0.5:ct=20,\
   vibrance=ib=0.2:ig=0.1:ir=-0.1,\
   colorbalance=rs=0.05:gs=0.02:bs=-0.03,\
   unsharp=5:5:0.8:3:3:0.4" \
  -c:a copy output_final.mp4
```

**各参数说明：**
- `smartblur`：lr=亮度半径, ls=亮度强度, lt=亮度阈值, cr=色度半径, cs=色度强度, ct=色度阈值。值越大磨皮越重，适当调整
- `vibrance`：ib=蓝色增强, ig=绿色增强, ir=红色减弱（肤色偏暖）
- `colorbalance`：rs=红色阴影, gs=绿色阴影, bs=蓝色阴影。微调让肤色自然
- `unsharp`：5:5:0.8 为亮度锐化强度, 3:3:0.4 为色度锐化

**完整美化管线参考见 `references/fashion-beautification-pipeline.md`**

### Step 4: TTS 旁白配音

**工具选择：**

| 工具 | 优先级 | 说明 |
|:-----|:------|:-----|
| **bailian-cli tts (CosyVoice)** | ⭐ 首选 | 中文 TTS 效果最好，自然流畅 |
| **Edge-TTS** | ⭐ 备选 | 免费，`pip install edge-tts` |
| **text_to_speech (Hermes内置)** | 兜底 | 配置的后端 TTS |
| **ElevenLabs** | 兜底 | 已配好 API Key |

**CosyVoice 调用：**
```bash
python ~/AppData/Local/hermes/scripts/bailian_cli.py tts "旁白文案内容" --model cosyvoice-v3-flash
# 输出：保存为 mp3 文件
```

**Edge-TTS 调用：**
```bash
edge-tts --text "旁白文案内容" --voice zh-CN-XiaoxiaoNeural --write-media output.mp3
```

**音色推荐（女装视频）：**
- 温柔知性风：zh-CN-XiaoxiaoNeural（Edge-TTS）
- 亲切闺蜜风：zh-CN-XiaoxuanNeural（Edge-TTS）
- CosyVoice 默认音色（自然，不分角色）

**多段音频拼接：**
```bash
# 如果有多段旁白，用 ffmpeg concat 拼接
ffmpeg -f concat -safe 0 -i <(for f in *.mp3; do echo "file '$PWD/$f'"; done) \
  -c copy narration_concat.mp3
```

### Step 5: 视频拼接 + 转场

**xfade 转场效果（推荐）：**

| 风格 | 推荐转场 | 适用场景 |
|:-----|:---------|:---------|
| 优雅 | fadeblack, dissolve, fadeslow | 服装展示间切换 |
| 时尚 | slideleft, slideright, coverleft | 不同角度展示 |
| 动感 | zoomin, circleopen, pixelize | 细节特写切换 |
| 柔和 | smoothleft, smoothright, fadewhite | 场景过渡 |

**基本用法：**
```bash
# 两个片段加转场（0.5秒过渡）
ffmpeg -i clip1.mp4 -i clip2.mp4 \
  -filter_complex "[0:v][1:v]xfade=transition=fadeblack:duration=0.5:offset=9.5[outv]" \
  -map "[outv]" -map 0:a -c:a copy -shortest output.mp4
```

**多片段拼接（使用 concat + xfade 混合策略）：**
- 多个片段时，先对每个片段做美颜处理
- 用 concat demuxer 拼接（无转场）或逐段 xfade（有转场）
- 复杂度高时，委托 video-use 的 render.py 处理

### Step 6: 字幕生成 + 烧录

**字幕生成：**
```python
# 旁白文案已有精确时间轴 → 直接生成 SRT
with open("subtitles.srt", "w", encoding="utf-8") as f:
    for i, (start, end, text) in enumerate(narration_segments, 1):
        f.write(f"{i}\n{start} --> {end}\n{text}\n\n")
```

**烧录字幕：**
```bash
# 软字幕（可关闭）
ffmpeg -i video.mp4 -i subtitles.srt -c copy -c:s mov_text output.mp4

# 硬字幕（已渲染到画面，不可关闭）
ffmpeg -i video.mp4 -vf "subtitles=subtitles.srt:fontsdir=/path/to/fonts:force_style='FontName=SimHei,FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,MarginV=60'" \
  -c:a copy output.mp4
```

**字幕样式：**
- 字体：SimHei（黑体）或微软雅黑，清晰易读
- 大小：18-22（视分辨率而定）
- 颜色：白色字+黑色描边（高对比度）
- 位置：底部 MarginV=60，不遮挡服装展示区域
- 中文字幕建议每行不超过 15 个字

### Step 7: 包装成片

**片头/片尾：**
```bash
# 用 image_generate 生成封面图（FAL FLUX）
# 提示词示例：大码女装穿搭视频封面，时尚简约，暖色调

# 片头叠加
ffmpeg -i main_video.mp4 -i intro.mp4 -i outro.mp4 \
  -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0[vid]" \
  -map "[vid]" -c:v libx264 output_final.mp4
```

**水印/Logo：**
```bash
ffmpeg -i video.mp4 -i logo.png \
  -filter_complex "overlay=W-w-10:10" \
  -c:a copy video_watermarked.mp4
```

## 工具清单

| 工具 | 用途 | 安装状态 |
|:-----|:-----|:-------- |
| **ffmpeg/ffprobe** | 视频处理核心（剪切/转场/滤镜/调色/字幕） | ✅ 已安装 |
| **video-use** | 完整剪辑管线（转录/EDL/渲染/自检） | ✅ 已安装 |
| **bailian-cli** | TTS 配音（CosyVoice）、ASR 转录 | ✅ 已安装 |
| **Edge-TTS** | 备用 TTS（免费中文） | 📦 需 `pip install edge-tts` |
| **image_generate (FAL)** | 片头/封面图生成 | ✅ 可用 |
| **GFPGAN** | 高级人脸修复（可选，单帧处理） | 📦 可选安装 |

## 常见坑（Pitfalls）

1. **美颜不要过度** — smartblur 的阈值（lt/ct）不要超过 20，否则画面变"塑料感"。服装视频需要保留面料纹理
2. **TTS 语速控制** — 中文 TTS 默认语速偏快，需调整。CosyVoice 暂无速度参数，Edge-TTS 用 `--rate=-10%` 减速
3. **旁白分段必须与片段对齐** — 每段旁白的时长必须精确匹配对应的视频片段时长，否则音画不同步
4. **转场不要堆砌** — 一个视频用 2-3 种转场风格即可，太多显得杂乱
5. **字幕不要遮挡服装** — 底部字幕的 MarginV 要足够大，确保不挡住服装展示区域（特别是下半身裙装）
6. **先做美颜再做转场** — 美颜处理每个片段，再做转场拼接。合并一步做会导致转场区域的美颜不均匀
7. **大码女装色彩策略** — 调色时注意深色服装容易丢失细节，适当提高阴影亮度；浅色服装注意不要过曝
8. **音频处理顺序** — 先加入 TTS 旁白，再加入背景音乐，最后做音量平衡（旁白 70% + 背景音乐 30%）

## 与 video-use 协同

本技能处理的是"从素材库挑选片段"的前端工作。选片完成后，具体的剪辑执行（EDL生成、渲染、自检）可以委托给 `video-use` 的 `render.py`。

**推荐分工：**
```
fashion-video-pipeline 负责：
  1. 素材分析 → 选片
  2. 剧本 + 旁白文案
  3. 美颜美化每个片段
  4. TTS 配音生成

video-use 负责：
  5. 转场拼接（EDL + render.py）
  6. 字幕烧录
  7. 成片输出
```

## 输出目录结构

```
<素材目录>/
├── <原始素材>/
├── edit/
│   ├── selected_clips/       ← 选中的片段（已美颜处理）
│   ├── narration/            ← TTS 旁白音频文件
│   ├── subtitles.srt         ← 字幕文件
│   ├── intro_outro/          ← 片头/片尾
│   ├── preview.mp4           ← 预览版
│   └── final.mp4             ← 最终成片
```