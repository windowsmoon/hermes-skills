#!/usr/bin/env python3
"""硅基流动 DeepSeek OCR + TTS 服务"""

import base64, json, os, sys, urllib.request

def get_key():
    env = os.path.expanduser("~/.hermes/.env")
    with open(env) as f:
        for line in f:
            if 'HINDSIGHT_LLM_API_KEY' in line:
                return line.split('=', 1)[1].strip()
    return ""

def api_siliconflow(path, data):
    key = get_key()
    req = urllib.request.Request(f"https://api.siliconflow.cn{path}",
        data=json.dumps(data).encode() if data else None,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode())

def ocr(image_path, prompt="请识别图中的文字"):
    """DeepSeek OCR - 识别图片中的文字"""
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    data = {
        "model": "deepseek-ai/DeepSeek-OCR",
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
        ]}]
    }
    result = api_siliconflow("/v1/chat/completions", data)
    return result["choices"][0]["message"]["content"]

def tts(text, voice="FunAudioLLM/CosyVoice2-0.5B"):
    """语音合成 TTS"""
    data = {"model": voice, "input": text}
    req = urllib.request.Request("https://api.siliconflow.cn/v1/audio/speech",
        data=json.dumps(data).encode(),
        headers={"Authorization": f"Bearer {get_key()}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        audio = resp.read()
        out = os.path.expanduser("~/Desktop/siliconflow_tts.mp3")
        with open(out, "wb") as f:
            f.write(audio)
        return f"语音已保存: {out} ({len(audio)/1024:.0f} KB)"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: sf_cli.py ocr <图片路径> [提示词]")
        print("       sf_cli.py tts <文字>")
        sys.exit(1)
    mode = sys.argv[1]
    if mode == "ocr":
        img = sys.argv[2]
        prompt = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else "请识别图中的文字"
        print(ocr(img, prompt))
    elif mode == "tts":
        text = " ".join(sys.argv[2:])
        print(tts(text))
