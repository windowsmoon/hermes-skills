# CLI Video Tools Catalog — Transitions, Beautification, Color Grading, MCP

## Purpose

This file catalogs the open-source CLI tools, libraries, and MCP servers available for video editing tasks beyond FFmpeg's built-in filters. Use it when a session needs transitions, AI beautification, dedicated color grading pipelines, or MCP-based video tooling.

---

## 1. VIDEO TRANSITIONS (beyond FFmpeg xfade)

| Tool | Type | Transitions | Key Command | Stars | Link |
|------|------|-------------|-------------|-------|------|
| **FFmpeg xfade** | Built-in CLI | 30+ types: fade, dissolve, slide, wipe, glitch, pixelize, radial, zoomin, squeeze, circle, etc. | `ffmpeg -i a.mp4 -i b.mp4 -filter_complex "xfade=transition=fade:duration=1:offset=5" out.mp4` | ★48k | github.com/FFmpeg/FFmpeg |
| **MLT melt** | CLI framework | Luma wipes, compositing transitions | `melt clip1.mp4 clip2.mp4 -transition luma file=luma.png -consumer avformat:out.mp4` | ★1k | github.com/mltframework/mlt |
| **Editly** | Node.js CLI | Crossfade, slide, wipe | `editly clip1.mp4 clip2.mp4 --transition crossfade --duration 5` | ★5k | github.com/mifi/editly |
| **MoviePy** | Python library | Crossfade, slide, compositing | `from moviepy.editor import *` | ★13k | github.com/Zulko/moviepy |
| **ffmpeg-concat** | Node.js CLI | GL transitions (WebGL shaders) | `ffmpeg-concat -t fade -o out.mp4 clip1.mp4 clip2.mp4` | ★500 | github.com/transitive-bullshit/ffmpeg-concat |

**FFmpeg xfade transition types**: `fade`, `fadeblack`, `fadewhite`, `dissolve`, `pixelize`, `slideright`, `slideleft`, `slideup`, `slidedown`, `smoothleft`, `smoothright`, `smoothup`, `smoothdown`, `circleclose`, `circleopen`, `horzclose`, `horzopen`, `vertclose`, `vertopen`, `diagbl`, `diagbr`, `diagtl`, `diagtr`, `radial`, `wipetl`, `wipetr`, `wipebl`, `wipebr`, `zoomin`, `squeezeh`, `squeezev`, `glitch`, `hblur`, `fadegrays`, `hlslice`, `hrslice`, `vuslice`, `vdslice`.

---

## 2. AI BEAUTIFICATION (Skin Smoothing, Face Restoration, Enhancement)

These go beyond FFmpeg's `smartblur` — they use deep learning models for superior results.

| Tool | Type | Best For | Key Command | Stars | Link |
|------|------|----------|-------------|-------|------|
| **OpenCV** | Python + CLI | Bilateral filter skin smoothing, DNN face beautification | `python -c "import cv2; ..."` | ★80k | github.com/opencv/opencv |
| **Real-ESRGAN** | Python CLI | AI upscaling + denoising (enhancement beautification) | `python inference_realesrgan.py -i input.mp4 -o output.mp4 -n RealESRGAN_x4plus` | ★28k | github.com/xinntao/Real-ESRGAN |
| **GFPGAN** | Python CLI | Face restoration, blemish removal, skin texture improvement | `python inference_gfpgan.py -i input.mp4 -o output.mp4 -v 1.4` | ★36k | github.com/TencentARC/GFPGAN |
| **CodeFormer** | Python CLI | Face restoration (alternative to GFPGAN, better for extreme degradation) | `python inference_codeformer.py -i input.mp4 -o output.mp4` | ★16k | github.com/sczhou/CodeFormer |
| **Waifu2x-ncnn-vulkan** | CLI (Vulkan) | Upscaling + denoising, GPU-accelerated | `waifu2x-ncnn-vulkan -i input.mp4 -o output.mp4 -n 2` | ★22k | github.com/nihui/waifu2x-ncnn-vulkan |

**Performance notes:**
- GFPGAN/CodeFormer process frame-by-frame — slow on CPU; GPU (CUDA) strongly recommended for video
- Real-ESRGAN is more efficient but still GPU-bound for real-time
- Waifu2x-ncnn-vulkan uses Vulkan (works on AMD/NVIDIA/Intel GPUs)

---

## 3. COLOR GRADING (CLI / Programmatic)

### FFmpeg built-in color filters

| Filter | Purpose | Example |
|--------|---------|---------|
| `colorbalance` | RGB channel balance | `colorbalance=rs=0.1:gs=-0.05:bs=-0.05` (warm look) |
| `curves` | Preset curves | `curves=vintage` / `curves=colornegative` / `curves=crossprocess` |
| `lut3d` | Apply .cube 3D LUT file | `lut3d=file=cinematic_look.cube` |
| `eq` | Brightness, saturation, contrast, gamma | `eq=brightness=0.05:saturation=1.2:contrast=1.1` |
| `colortemperature` | Color temperature (Kelvin-based) | `colortemperature=3500` (warm) / `colortemperature=-1500` (cool) |
| `colorchannelmixer` | Per-channel mixing | `colorchannelmixer=rr=1.2:gg=0.9:bb=0.8` |
| `colorlevels` | Per-channel levels | `colorlevels=rimin=0.05:gimin=0.05:bimin=0.05` |
| `colorize` | Hue/saturation tint | `colorize=hue=0:saturation=0.5` |
| `hue` | Hue shift | `hue=H=10` |
| `gradfun` | Gradient-based dithering | `gradfun=strength=1.5` |

### Dedicated color grading tools

| Tool | Type | Description | Link |
|------|------|-------------|------|
| **OpenColorIO (OCIO)** | CLI (`ocioconvert`) | Industry standard color management. Supports ACES, sRGB, Rec.709, etc. | github.com/AcademySoftwareFoundation/OpenColorIO (★2k) |
| **Colour Science** | Python library | Professional color science: transforms, grading, LUT generation | github.com/colour-science/colour (★2k) |
| **ImageMagick** | CLI (`magick`) | Frame-based color matrix transformations | `magick frame.png -color-matrix "1.2 0 0 0, 0 1.1 0 0, 0 0 0.9 0" out.png` |

**CLI examples:**
```bash
# Warm cinematic look
ffmpeg -i input.mp4 -vf "colorbalance=rs=0.1:gs=-0.05:bs=-0.05" output.mp4

# Apply 3D LUT
ffmpeg -i input.mp4 -vf "lut3d=file=cinematic_look.cube" output.mp4

# Full eq adjust
ffmpeg -i input.mp4 -vf "eq=brightness=0.05:saturation=1.2:contrast=1.1:gamma=1.0" output.mp4

# Vintage curve
ffmpeg -i input.mp4 -vf "curves=vintage" output.mp4
```

---

## 4. MCP (Model Context Protocol) Servers for Video

Community MCP servers that wrap video tools for LLM-based editing:

| MCP Server | Backend | Capabilities | Status |
|------------|---------|--------------|--------|
| **mcp-ffmpeg** | FFmpeg | Transitions, trimming, color grading, filters | Community |
| **mcp-moviepy** | MoviePy | Programmatic editing, compositing, transitions | Community |
| **mcp-video-edit** | FFmpeg | General video editing operations | Community |
| **mcp-editly** | Editly | Node.js-based transitions pipeline | Community |
| **mcp-shotstack** | Shotstack API | Cloud-based editing (commercial API) | Community |

All are early-stage. Search GitHub for `mcp video` or `mcp ffmpeg` to find the latest repos.

---

## 5. COMPREHENSIVE VIDEO PLATFORMS (CLI / API)

| Tool | Type | Stars | License | Link |
|------|------|-------|---------|------|
| **Remotion** | React-based video rendering | ★22k | MIT | github.com/remotion-dev/remotion |
| **Auto-Editor** | CLI auto editing (silence removal, cuts) | ★8k | MIT | github.com/WyattBlue/auto-editor |
| **LosslessCut** | CLI/GUI lossless trimming | ★30k | MIT | github.com/mifi/lossless-cut |
| **Shotstack** | REST API (commercial, free tier) | — | Commercial | shotstack.io |
| **Veed.io** | REST API (commercial) | — | Commercial | veed.io |

---

## 6. RECOMMENDED PIPELINES

### AI beautification pipeline:
```
Input → FFmpeg smartblur (basic smoothing) → GFPGAN (face restoration) → FFmpeg unsharp (sharpening) → Output
```

### Transition pipeline:
```
Input clips → Editly / ffmpeg-concat / xfade → Output (with transitions between clips)
```

### Color grading pipeline:
```
Input → FFmpeg eq (base correction) → FFmpeg lut3d (LUT) → FFmpeg curves (creative grade) → Output
```

### MCP-powered agent pipeline:
```
LLM → mcp-ffmpeg (transitions, grading, trimming) + mcp-moviepy (beautification)
```

---

## 7. KEY GITHUB SEARCH QUERIES

| Query | For |
|-------|-----|
| `ffmpeg xfade transition` | FFmpeg transition docs |
| `video beautification open source` | Beauty/skin smoothing repos |
| `color grading CLI tool` | LUT tools and color science |
| `mcp video editing server` | MCP video tool repos |
| `editly npm transitions` | Editly documentation |
| `moviepy transitions` | MoviePy transition docs |
| `GFPGAN video` | Face restoration for video |
| `Real-ESRGAN video` | Video enhancement |

---

*Research compiled July 2026. Star counts and URLs based on last known public data; verify current status on GitHub before depending on a tool.*

## 8. WINDOWS INSTALLATION PITFALLS (Hermes Agent)

### GFPGAN / Real-ESRGAN

```bash
# 安装顺序（Hermes 自带 Python 3.12.13）
pip install gfpgan realesrgan -i https://pypi.tuna.tsinghua.edu.cn/simple --no-deps
pip install facexlib -i https://pypi.tuna.tsinghua.edu.cn/simple
# basicsr 需要单独安装（无预编译 wheel，需从源码构建）
pip install basicsr -i https://pypi.tuna.tsinghua.edu.cn/simple --no-deps --no-build-isolation
```

**⚠️ 关键补丁：** basicsr 1.4.2 安装后，`site-packages/basicsr/data/degradations.py` 中有 `from torchvision.transforms.functional_tensor import rgb_to_grayscale`，在 torchvision 2.8.0+ 中该模块已合并到 `functional`。需手动替换为：
```python
from torchvision.transforms.functional import rgb_to_grayscale
```

**⚠️ numpy 版本冲突：** gfpgan 依赖 numpy<1.21，但 whisper 需要 numpy>=2.0。用 `--no-deps` 安装 gfpgan 可跳过此冲突。

### Real-ESRGAN ncnn-vulkan 二进制

- 下载 `realesrgan-ncnn-vulkan-v0.2.0-windows.zip` 解压后，将 `realesrgan-ncnn-vulkan.exe` + `vcomp140.dll` 复制到 Hermes 的 `node/` 目录
- **需要 Vulkan 运行时**（`vulkan-1.dll`）。如果系统未安装，运行会报 `exit=3221225781`。此时回退到 Python 版 `realesrgan`（CPU 运行，速度较慢但功能一致）

### 国内网络环境

- 所有 pip 安装使用清华镜像：`-i https://pypi.tuna.tsinghua.edu.cn/simple`
- GitHub release 下载慢时，可用 `ghproxy.com` 镜像
- Edge-TTS 无需镜像，直接 `pip install edge-tts` 即可