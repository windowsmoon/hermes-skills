#!/usr/bin/env python3
"""智能PPT生成 - 文多多出大纲，详参走ChatPPT"""
import json, os, sys, time, urllib.request, subprocess, tempfile

CONFIG = os.path.expanduser("~/.aippt_config.json")
BASE = "https://docmee.cn"
UID = "test"
CHATPPT = "C:\\Users\\Admin\\AppData\\Roaming\\npm\\node_modules\\@yooai\\cli\\bin\\chatppt.exe"

def load_key():
    with open(CONFIG) as f:
        return json.load(f)["api_key"]

def api_json(path, data=None, method="POST", token=None):
    key = load_key()
    h = {"Content-Type": "application/json", "User-Agent": "PPT"}
    if token: h["token"] = token
    else: h["Api-Key"] = key
    b = json.dumps(data).encode() if data else None
    r = urllib.request.Request(f"{BASE}{path}", data=b, method=method, headers=h)
    with urllib.request.urlopen(r, timeout=120) as resp:
        return json.loads(resp.read().decode())

def api_sse(path, data, token):
    h = {"Content-Type": "application/json", "token": token}
    b = json.dumps(data).encode()
    r = urllib.request.Request(f"{BASE}{path}", data=b, method="POST", headers=h)
    text = ""
    with urllib.request.urlopen(r, timeout=180) as resp:
        while True:
            line = resp.readline()
            if not line: break
            ln = line.decode("utf-8", errors="replace").strip()
            if ln.startswith("data:"):
                try:
                    d = json.loads(ln[5:])
                    if "text" in d: text += d["text"]
                    if d.get("status") == -1: return {"error": d.get("error","")}
                except: pass
    return {"data": text}

def chatppt_run(cmd, timeout=300):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    for line in r.stdout.split("\n"):
        if line.startswith("{"):
            return json.loads(line)
    return {"error": r.stdout[:500]}

def run(mode, subject, extra_text=""):
    combined = subject + ("\n\n" + extra_text if extra_text else "")
    t = api_json("/api/user/createApiToken", {"uid": UID}).get("data",{}).get("token")
    if not t: return {"error":"Token失败"}
    outline = api_sse("/api/ppt/generateOutline", {"subject": combined}, t)
    o = outline.get("data","")
    if not o: return {"error":"大纲失败","detail":outline}
    if mode == "simple":
        content = api_sse("/api/ppt/generateContent", {"subject": combined}, t)
        md = content.get("data","")
        tid = api_json("/api/ppt/randomTemplateId", method="GET", token=t).get("data",{}).get("id")
        ppt = api_json("/api/ppt/generatePptx", {"templateId": tid, "markdown": md}, token=t)
        pid = ppt.get("data",{}).get("id")
        dl = api_json(f"/api/ppt/downloadPptx?id={pid}", method="GET", token=t)
        return {"mode":"simple","subject":subject,"download_url":dl.get("data",{}).get("fileUrl")}
    elif mode == "elaborate":
        out_file = os.path.join(tempfile.gettempdir(), f"outline_{int(time.time())}.md")
        with open(out_file, "w", encoding="utf-8") as f: f.write(o)
        return {"mode":"elaborate","subject":subject,"outline_file":out_file}
    return {"error":"unknown"}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: smart_ppt.py simple|elaborate <subject> [extra_file]")
        sys.exit(1)
    mode, subject = sys.argv[1], sys.argv[2]
    extra = ""
    if len(sys.argv) > 3:
        fpath = sys.argv[3]
        if os.path.exists(fpath):
            with open(fpath, encoding="utf-8") as f: extra = f.read()
    result = run(mode, subject, extra)
    print(json.dumps(result, ensure_ascii=False, indent=2))
