#!/usr/bin/env python3
"""
飞书多维表格附件 tmp_download_url 批量获取脚本
用法: python get_bitable_urls.py <app_id> <app_secret> <app_token> <table_id> [record_id]

输出 JSON 格式:
  {
    "图片": ["文件名||tmp_url", ...],
    "音频": ["文件名||tmp_url", ...],
    "视频": ["文件名||tmp_url", ...],
    "_all_urls": {"文件名": "tmp_url", ...}
  }

示例:
  python get_bitable_urls.py cli_a851f4d520a8900b ***FEISHU_SECRET*** HeYWbu1Ppa2MEWs9AjJc09WJnce tblEsoWpihj5JwM3 recvnJQRxyUvTz
"""

import urllib.request, urllib.parse, json, time, os, sys

def get_token(app_id, app_secret):
    data = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read())
    if result.get("code") != 0:
        raise RuntimeError(f"获取 token 失败: {result}")
    return result["tenant_access_token"]

def get_fields(token, app_token, table_id):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read())
    name_to_type = {}
    for f in result.get("data", {}).get("items", []):
        name_to_type[f["field_name"]] = f["type"]
    return name_to_type

def get_records(token, app_token, table_id):
    url = (f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}"
           f"/records?page_size=100&field_names=true")
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read())
    return result.get("data", {}).get("items", [])

def get_record(token, app_token, table_id, record_id):
    url = (f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}"
           f"/records/{record_id}?field_names=true")
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read())
    return result.get("data", {}).get("record", {})

def get_tmp_url(token, file_token):
    params = urllib.parse.urlencode({
        "file_tokens": file_token,
        "extra": '{"bitablePermission":"bitable_file_download_token"}'
    })
    url = f"https://open.feishu.cn/open-apis/drive/v1/medias/batch_get_tmp_download_url?{params}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read())
    urls = result.get("data", {}).get("tmp_download_urls", [])
    return urls[0]["tmp_download_url"] if urls else None

_EXT = {
    ".jpg": "图片", ".jpeg": "图片", ".png": "图片", ".gif": "图片", ".webp": "图片",
    ".bmp": "图片", ".svg": "图片",
    ".mp3": "音频", ".wav": "音频", ".aac": "音频", ".m4a": "音频",
    ".flac": "音频", ".ogg": "音频", ".amr": "音频",
    ".mp4": "视频", ".mov": "视频", ".avi": "视频", ".mkv": "视频",
    ".webm": "视频", ".flv": "视频", ".wmv": "视频",
}

def classify(name):
    return _EXT.get(os.path.splitext(name)[1].lower())

def process_record(token, app_token, table_id, record_id):
    name_to_type = get_fields(token, app_token, table_id)
    record = get_record(token, app_token, table_id, record_id)
    fields = record.get("fields", {})
    result = {"图片": [], "音频": [], "视频": [], "_all_urls": {}}
    for fn, fv in fields.items():
        if fv is None or not isinstance(fv, list):
            continue
        if name_to_type.get(fn) != 17:
            continue
        for item in fv:
            if not isinstance(item, dict):
                continue
            ft = item.get("file_token")
            name = item.get("name", ft or "")
            if not ft:
                continue
            url = get_tmp_url(token, ft)
            time.sleep(0.2)
            if url:
                entry = f"{name}||{url}"
                result["_all_urls"][name] = url
                cat = classify(name)
                if cat:
                    result[cat].append(entry)
    return result

def main():
    if len(sys.argv) < 5:
        print(json.dumps({"error": "用法: python get_bitable_urls.py <app_id> <app_secret> <app_token> <table_id> [record_id]"}))
        sys.exit(1)
    app_id, app_secret = sys.argv[1], sys.argv[2]
    app_token, table_id = sys.argv[3], sys.argv[4]
    record_id = sys.argv[5] if len(sys.argv) > 5 else None
    token = get_token(app_id, app_secret)
    if record_id:
        result = process_record(token, app_token, table_id, record_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        records = get_records(token, app_token, table_id)
        merged = {"图片": [], "音频": [], "视频": [], "_all_urls": {}}
        for rec in records:
            r = process_record(token, app_token, table_id, rec["record_id"])
            for k in ["图片", "音频", "视频"]:
                merged[k].extend(r[k])
            merged["_all_urls"].update(r["_all_urls"])
        print(json.dumps(merged, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()