#!/usr/bin/env python3
"""AiPPT CLI — 通过 docmee.cn 开放平台 API 生成 PPT"""

import json, os, sys, time, urllib.request, urllib.error

CONFIG = os.path.expanduser("~/.aippt_config.json")
BASE = "https://docmee.cn"
UID = "hermes_agent"

def load_key():
    with open(CONFIG) as f:
        return json.load(f)["api_key"]

def req(path, data=None, method="POST", extra_headers=None):
    key = load_key()
    url = f"{BASE}{path}"
    body = json.dumps(data).encode() if data else None
    headers = {"Content-Type": "application/json", "User-Agent": "AiPPT-CLI"}
    if extra_headers:
        headers.update(extra_headers)
    else:
        headers["Api-Key"] = key
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode())

def create_token():
    r = req("/api/user/createApiToken", {"uid": UID, "limit": None},
            extra_headers={"Api-Key": load_key()})
    if r.get("code") != 0:
        raise Exception(r.get("message", "创建token失败"))
    return r["data"]["token"]

def cmd_templates(token):
    r = req("/api/ppt/randomTemplateId", extra_headers={"token": token})
    return r.get("data", {}).get("id")

def generate_outline(token, subject):
    sb = []
    r = req("/api/ppt/generateOutline", {"subject": subject, "dataUrl": None, "prompt": None},
            extra_headers={"token": token})
    return r

def cmd_info():
    key = load_key()
    r = req("/api/user/createApiToken", {"uid": UID, "limit": None},
            extra_headers={"Api-Key": key})
    if r.get("code") == 0:
        print(f"✅ API Key 有效")
        print(f"Token: {r['data']['token'][:20]}...")
    else:
        print(f"❌ {r.get('message', '未知错误')}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: aippt_cli.py <命令> [参数]")
        print("  info          验证 API Key")
        print("  generate <主题>  生成 PPT")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "info":
        cmd_info()
    elif cmd == "generate":
        subject = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "默认主题"
        token = create_token()
        print(f"Token: {token[:30]}...")
        r = generate_outline(token, subject)
        print(f"大纲: {str(r)[:500]}")
