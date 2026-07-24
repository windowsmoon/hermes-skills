#!/usr/bin/env python3
"""百炼 CLI — 通过 DashScope API 调用阿里云百炼全模态能力"""

import argparse, base64, json, os, sys, urllib.request

API_KEY = "sk-325662f42be24e558aa8a00bf89cd3b1"
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

def api(url, data, timeout=120):
    req = urllib.request.Request(url, json.dumps(data).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())

def chat(text, model="qwen3.7-plus", system=""):
    msgs = []
    if system: msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": text})
    r = api(f"{BASE_URL}/chat/completions", {"model": model, "messages": msgs, "temperature": 0.7})
    return r["choices"][0]["message"]["content"]

def vision(path, prompt="描述图片", model="qwen3-vl-plus"):
    if path.startswith(("http://", "https://")):
        with urllib.request.urlopen(path) as r:
            b64 = base64.b64encode(r.read()).decode()
    else:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
    msgs = [{"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
        {"type": "text", "text": prompt}
    ]}]
    r = api(f"{BASE_URL}/chat/completions", {"model": model, "messages": msgs})
    return r["choices"][0]["message"]["content"]

def image(prompt, model="qwen-image-2.0"):
    r = api("https://dashscope.aliyuncs.com/api/v1/services/aigc/image-generation/generation",
        {"model": model, "input": {"prompt": prompt}})
    urls = [x.get("url") for x in r.get("output", {}).get("results", []) if x.get("url")]
    return "\n".join(urls) if urls else str(r)

def search(query):
    r = api("https://dashscope.aliyuncs.com/api/v1/services/web-search/search",
        {"model": "qwen-web-search", "input": {"query": query}}, timeout=60)
    return r.get("output", {}).get("result", str(r))

def tts(text, voice="cosyvoice-v3-flash"):
    r = api("https://dashscope.aliyuncs.com/api/v1/services/audio/tts/synthesis",
        {"model": voice, "input": {"text": text}, "parameters": {"format": "mp3"}})
    audio = r.get("output", {}).get("audio", "")
    if audio:
        out = os.path.expanduser("~/Desktop/bailian_tts.mp3")
        with open(out, "wb") as f:
            f.write(base64.b64decode(audio))
        return f"语音已保存: {out}"
    return str(r)

def asr(file):
    with open(file, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    r = api("https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription",
        {"model": "qwen3-asr-flash", "input": {"audio": b64}})
    return r.get("output", {}).get("text", str(r))

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="百炼 CLI")
    p.add_argument("mode", choices=["chat","vision","image","search","tts","asr","models"])
    p.add_argument("input", nargs="*")
    p.add_argument("--model", "-m", default=None)
    p.add_argument("--system", "-s", default="")
    p.add_argument("--file", "-f", default=None)
    a = p.parse_args()
    t = " ".join(a.input) if a.input else ""
    
    if a.mode == "models":
        print("文本: qwen3.7-plus | 视觉: qwen3-vl-plus | 生图: qwen-image-2.0 | 搜索: qwen-web-search | ASR: qwen3-asr-flash | TTS: cosyvoice-v3-flash")
    elif a.mode == "chat":
        print(chat(t, a.model or "qwen3.7-plus", a.system))
    elif a.mode == "vision":
        print(vision(a.file, t, a.model or "qwen3-vl-plus"))
    elif a.mode == "image":
        print(image(t, a.model or "qwen-image-2.0"))
    elif a.mode == "search":
        print(search(t))
    elif a.mode == "tts":
        print(tts(t))
    elif a.mode == "asr":
        print(asr(a.file))
