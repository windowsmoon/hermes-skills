#!/usr/bin/env python3
"""
大码女装视频混剪管线 — 完整执行脚本
选片→编排→TTS配音→字幕→剪映草稿生成
"""
import os, sys, json, subprocess, tempfile, re, uuid, time
from pathlib import Path

# ============================================================
# Phase 1: 素材分析
# ============================================================
def analyze_clips(clips_dir):
    """分析素材目录中的所有视频文件"""
    video_exts = {'.mp4', '.mov', '.avi', '.webm', '.mkv', '.flv', '.m4v'}
    clips = []
    
    for f in sorted(os.listdir(clips_dir)):
        ext = os.path.splitext(f)[1].lower()
        if ext in video_exts:
            fp = os.path.join(clips_dir, f)
            size_mb = os.path.getsize(fp) / 1024 / 1024
            clips.append({"file": f, "path": fp, "size_mb": round(size_mb, 1), "ext": ext})
    
    return clips

def get_clip_info(clip_path):
    """用 ffprobe 获取视频信息"""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", clip_path],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode == 0:
        return json.loads(result.stdout)
    return {}

def extract_audio(clip_path, output_dir):
    """用 ffmpeg 提取音频"""
    audio_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(clip_path))[0]}.wav")
    if not os.path.exists(audio_path):
        subprocess.run(
            ["ffmpeg", "-i", clip_path, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", audio_path, "-y"],
            capture_output=True, timeout=60
        )
    return audio_path

def transcribe_clip(audio_path, whisper_model=None):
    """用 Whisper 转录音频"""
    try:
        import whisper
        if whisper_model is None:
            model = whisper.load_model("base")
        result = model.transcribe(audio_path, language="zh")
        return result["text"].strip()
    except Exception as e:
        return f"[转录失败: {e}]"

def extract_keyframe(clip_path, output_dir, time_sec=3):
    """用 ffmpeg 提取关键帧"""
    keyframe_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(clip_path))[0]}_keyframe.jpg")
    if not os.path.exists(keyframe_path):
        subprocess.run(
            ["ffmpeg", "-ss", str(time_sec), "-i", clip_path, "-vframes", "1", "-q:v", "2", keyframe_path, "-y"],
            capture_output=True, timeout=30
        )
    return keyframe_path if os.path.exists(keyframe_path) else None

# ============================================================
# Phase 2: 选片+编排 (LLM 驱动)
# ============================================================
def select_and_arrange(clips_info, topic, selling_points):
    """
    LLM 根据素材内容选择最佳片段并编排顺序
    返回编排方案
    """
    # 构建素材目录文本
    catalog_text = "\n".join([
        f"片段{i+1}: {c['file']} ({c['duration']}秒)"
        + (f"\n  转录内容: {c['transcript'][:200]}" if c.get('transcript') else "")
        for i, c in enumerate(clips_info)
    ])
    
    prompt = f"""你是一个大码女装穿搭视频剪辑师。
请从以下素材片段中，选出最能体现「{topic}」主题的片段，并按讲故事的方式编排顺序。

卖点：{selling_points}

素材目录：
{catalog_text}

请输出编排方案（JSON格式）：
{{
  "storyline": "一句话故事线",
  "selected_clips": [
    {{
      "index": 0,
      "file": "文件名",
      "reason": "为什么选这个片段",
      "narration_keywords": "这个片段时旁白要突出的关键词"
    }}
  ],
  "expected_duration_seconds": 预计总时长
}}

只输出 JSON，不要其他内容。
"""
    # 这里会在 Hermes 中由 LLM 实际执行，脚本只做框架
    return prompt


# ============================================================
# Phase 3: 旁白文案 + TTS
# ============================================================
def generate_narration(storyboard, selling_points, topic):
    """生成旁白文案"""
    clips_desc = "\n".join([
        f"片段{c['index']+1}: {c['file']} - {c.get('reason', '')} (关键词: {c.get('narration_keywords', '')})"
        for c in storyboard.get('selected_clips', [])
    ])
    
    prompt = f"""你是一个大码女装穿搭视频的文案策划。
请为以下编排方案写一段 30-60 秒的旁白文案。

主题：{topic}
卖点：{selling_points}
故事线：{storyboard.get('storyline', '')}

片段顺序：
{clips_desc}

要求：
- 口语化，像闺蜜聊天一样自然
- 突出显瘦、遮肚子、遮大腿、提气质
- 每个片段对应 8-15 秒旁白
- 总时长 30-60 秒
- 输出格式：每行一段话，标注对应片段名

格式：
[片段名] 旁白内容
"""
    return prompt

def tts_generate(text, output_path, voice="zh-CN-XiaoxiaoNeural"):
    """用 Edge-TTS 生成配音"""
    try:
        import edge_tts
        import asyncio
        
        async def _tts():
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
        
        asyncio.run(_tts())
        return True
    except Exception as e:
        print(f"TTS 失败: {e}")
        return False

def generate_srt(narration_segments, output_path):
    """生成 SRT 字幕文件"""
    lines = []
    for i, seg in enumerate(narration_segments, 1):
        start = seg.get("start", 0)
        end = seg.get("end", start + 3)
        text = seg.get("text", "")
        
        def to_srt(seconds):
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = int(seconds % 60)
            ms = int((seconds % 1) * 1000)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
        
        lines.append(f"{i}")
        lines.append(f"{to_srt(start)} --> {to_srt(end)}")
        lines.append(text)
        lines.append("")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

# ============================================================
# Phase 4: 生成剪映草稿 (pyJianYingDraft)
# ============================================================
def generate_capcut_draft(clips_info, storyboard, narration_path, srt_path, output_dir, draft_name):
    """用 pyJianYingDraft 生成剪映草稿"""
    try:
        import pyJianYingDraft as draft
        
        # 获取剪映草稿目录
        home = os.path.expanduser("~")
        draft_base = os.path.join(home, "AppData", "Local", "JianyingPro", "User Data", "Projects", "com.lveditor.draft")
        if not os.path.exists(draft_base):
            draft_base = os.path.join(home, "AppData", "Local", "JianyingPro", "Drafts")
        
        draft_dir = os.path.join(draft_base, draft_name)
        os.makedirs(draft_dir, exist_ok=True)
        
        # 创建新草稿
        script = draft.ScriptFile(draft_dir)
        
        # 添加选中的视频片段
        selected = storyboard.get("selected_clips", [])
        for i, clip_info in enumerate(selected):
            clip_path = clip_info.get("path", "")
            if os.path.exists(clip_path):
                # 添加视频轨道
                video_seg = draft.VideoSegment(
                    clip_path,
                    start=draft.time_span(0, 0, 0),
                    duration=draft.time_span(0, 0, min(15, clip_info.get("duration", 10)))
                )
                script.add_track(video_seg, track_index=i)
                
                # 添加转场（除了第一个片段）
                if i > 0:
                    transitions = ["slideleft", "slideright", "zoomin", "wipeleft", "smoothleft"]
                    trans = transitions[i % len(transitions)]
                    script.add_transition(trans, clip_index=i, duration=draft.time_span(0, 0, 0.5))
        
        # 添加配音音频
        if os.path.exists(narration_path):
            audio_seg = draft.AudioSegment(narration_path)
            script.add_track(audio_seg, track_index=len(selected))
        
        # 添加字幕
        if os.path.exists(srt_path):
            script.import_srt(srt_path, track_name="字幕")
        
        # 添加文本标题
        title_text = draft.TextSegment(
            "大码女装穿搭",
            start=draft.time_span(0, 0, 0),
            duration=draft.time_span(0, 0, 3),
            text_style=draft.TextStyle(size=15, bold=True, color=(1, 1, 1))
        )
        script.add_track(title_text, track_index=0)
        
        # 保存草稿
        script.save()
        return draft_dir
        
    except ImportError:
        print("pyJianYingDraft 未安装，回退到手动模式")
        return None
    except Exception as e:
        print(f"生成剪映草稿失败: {e}")
        return None

# ============================================================
# 主流程
# ============================================================
def main():
    print("=" * 60)
    print("大码女装视频混剪管线")
    print("=" * 60)
    print()
    print("使用方式：在 Hermes 中运行")
    print("  python scripts/pipeline.py <素材目录> [选项]")
    print()
    print("选项:")
    print("  --mode simple|full    混剪模式 (默认 simple)")
    print("  --topic <主题>        视频主题 (默认 大码女装穿搭)")
    print('  --selling <卖点>      卖点，逗号分隔 (默认 显瘦,遮肚子,遮大腿,提气质)')
    print("  --output <目录>       输出目录 (默认 素材目录/output)")
    print()

if __name__ == "__main__":
    main()