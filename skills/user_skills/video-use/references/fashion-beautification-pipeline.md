# 视频美颜美化管线 — ffmpeg + AI 工具链参考

## 本文件用途

记录本会话中调研的 ffmpeg 美颜美化滤镜链 + AI 人脸修复工具（GFPGAN/Real-ESRGAN），供 future sessions 在 fashion-video-pipeline 或 video-use 中直接使用。

## AI 美颜工具（GFPGAN + Real-ESRGAN）

需安装依赖：`pip install gfpgan realesrgan basicsr facexlib -i https://pypi.tuna.tsinghua.edu.cn/simple --no-deps`（basicsr 需单独用 --no-deps --no-build-isolation 安装）

### Windows 安装注意事项

1. **basicsr 需要 torchvision 补丁**：basicsr 1.4.2 的 `degradations.py` 中有 `from torchvision.transforms.functional_tensor import rgb_to_grayscale`，在 torchvision 2.8.0+ 中需改为 `from torchvision.transforms.functional import rgb_to_grayscale`。安装后手动修改 `site-packages/basicsr/data/degradations.py`。
2. **Real-ESRGAN ncnn-vulkan 二进制**需要 Vulkan 运行时。如果系统未安装 Vulkan，用 Python 版 `realesrgan` 替代（CPU 运行，速度较慢但功能一致）。
3. **模型权重**首次使用自动下载到 `~/.cache/gfpgan/` 和 `~/.cache/realesrgan/`，约 100-300MB。

### AI 美颜用法

```python
from gfpgan import GFPGANer
from realesrgan import RealESRGANer
import cv2, torch

# GFPGAN 人脸修复
model = GFPGANer(model_path='GFPGANv1.4.pth', upscale=1, arch='clean', channel_multiplier=2)
img = cv2.imread('frame.jpg')
_, _, restored = model.enhance(img, has_aligned=False, only_center_face=False, paste_back=True)

# Real-ESRGAN 超分辨率
upsampler = RealESRGANer(scale=4, model_path='RealESRGAN_x4plus.pth', tile=0, tile_pad=10, pre_pad=0)
img, _ = upsampler.enhance(img, outscale=4)
```

## 完整美颜管线（ffmpeg + AI）

```bash
# 管线推荐顺序：
# 输入 → ffmpeg smartblur（基础磨皮）→ GFPGAN（人脸修复，可选）→ ffmpeg unsharp（锐化）→ ffmpeg eq（调色）→ 输出
# 注意：GFPGAN/Real-ESRGAN 处理视频需逐帧，建议用 ffmpeg 提取帧 → AI 处理 → ffmpeg 合成回视频
```

## 滤镜效果速查

| 滤镜 | 用途 | 参数要点 |
|:-----|:-----|:---------|
| `smartblur` | 皮肤磨皮（保留边缘） | lr=亮度半径, ls=强度, lt=阈值(≤10不过度) |
| `vibrance` | 饱和度增强（不过曝） | ib=蓝, ig=绿, ir=红。负值减饱和 |
| `colorbalance` | 肤色校正/色温调整 | rs=红阴影, gs=绿阴影, bs=蓝阴影, 微调幅度 |
| `eq` | 亮度/对比度/伽马 | brightness/contrast/gamma/saturation |
| `curves` | 曲线调色（精细控制） | 支持 RGB 独立曲线 |
| `colortemperature` | 色温调整 | 正值偏暖，负值偏冷 |
| `huesaturation` | 色相/饱和度/亮度 | 可针对特定颜色范围调整 |
| `unsharp` | 锐化（提清晰度） | 5:5:0.8 亮度锐化, 3:3:0.4 色度锐化 |
| `nlmeans` | 降噪（保留细节） | 适合低光环境 |
| `hqdn3d` | 3D 降噪（时空域） | 空间+时间维度降噪 |

## 标准美颜管线（4步）

### 完整命令（一次编码，推荐）

```bash
ffmpeg -i input.mp4 -vf \
  "smartblur=lr=2.0:ls=0.5:lt=10:cr=1.0:cs=0.5:ct=20,\
   vibrance=ib=0.2:ig=0.1:ir=-0.1,\
   colorbalance=rs=0.05:gs=0.02:bs=-0.03,\
   unsharp=5:5:0.8:3:3:0.4" \
  -c:a copy -c:v libx264 -crf 18 -preset medium output.mp4
```

### 分步说明

**Step 1: 皮肤磨皮**
```bash
ffmpeg -i input.mp4 -vf "smartblur=lr=2.0:ls=0.5:lt=10:cr=1.0:cs=0.5:ct=20" -c:a copy step1.mp4
```
- `lr=2.0` — 亮度模糊半径（越大越糊）
- `ls=0.5` — 亮度模糊强度
- `lt=10` — 亮度阈值（≤10 保留边缘，不变成"塑料脸"）
- `cr=1.0` — 色度模糊半径
- `cs=0.5` — 色度模糊强度
- `ct=20` — 色度阈值

**Step 2: 颜色增强**
```bash
ffmpeg -i step1.mp4 -vf "vibrance=ib=0.2:ig=0.1:ir=-0.1" -c:a copy step2.mp4
```
- `ib=0.2` — 蓝色增强（天空/蓝色服装）
- `ig=0.1` — 绿色增强
- `ir=-0.1` — 红色减弱（避免肤色过红）

**Step 3: 肤色校正**
```bash
ffmpeg -i step2.mp4 -vf "colorbalance=rs=0.05:gs=0.02:bs=-0.03" -c:a copy step3.mp4
```
- `rs=0.05` — 红色阴影微增（提气色）
- `gs=0.02` — 绿色阴影微增
- `bs=-0.03` — 蓝色阴影微减（去黄）

**Step 4: 锐化**
```bash
ffmpeg -i step3.mp4 -vf "unsharp=5:5:0.8:3:3:0.4" -c:a copy step4.mp4
```
- `5:5:0.8` — luma_msize:luma_amount:luma_threshold（锐化强度）
- `3:3:0.4` — chroma_msize:chroma_amount:chroma_threshold

## 服装视频专用调色

### 深色服装（黑色/深蓝/深灰）
```bash
# 提升阴影细节，避免一片黑
ffmpeg -i input.mp4 -vf "eq=brightness=0.02:contrast=1.05:gamma=1.1" -c:a copy output.mp4
```

### 浅色服装（白色/米色/浅粉）
```bash
# 降低高光，避免过曝
ffmpeg -i input.mp4 -vf "eq=brightness=-0.02:gamma=0.95" -c:a copy output.mp4
```

### 大码女装通用调色
```bash
# 暖色调 + 柔和对比，显肤色好
ffmpeg -i input.mp4 -vf \
  "colortemperature=3500,\
   curves=master='0/0 0.1/0.08 0.5/0.52 0.9/0.92 1/1',\
   eq=saturation=1.1:brightness=0.01" \
  -c:a copy output.mp4
```

## 参数调节原则

1. **先试小值** — 所有参数从最小值开始，观察效果后再加
2. **皮肤优先** — 服装视频的调色以肤色自然为第一优先级，不能为了服装颜色牺牲肤色
3. **保留纹理** — 服装面料纹理（蕾丝/针织/牛仔/丝绸）要保留，不能磨皮过度抹平
4. **一致性** — 同一视频的不同片段要用相同的滤镜参数，避免切换时色差明显
5. **测试帧** — 用 `ffmpeg -ss 10 -i input.mp4 -frames:v 1 -q:v 2 test.jpg` 提取单帧测试滤镜效果，再应用到全片