#!/usr/bin/env python3
"""
飞书多维表格附件 tmp_download_url 批量获取脚本

用法:
  python get_bitable_urls.py <app_id> <app_secret> <app_token> <table_id> [record_id]

  - app_id / app_secret: 飞书应用的凭证
  - app_token / table_id: 多维表格地址中提取
  - record_id (可选): 不传则处理表格所有记录

输出 JSON 格式:
  {
    "图片": ["文件名||tmp_url", ...],
    "音频": ["文件名||tmp_url", ...],
    "视频": ["文件名||tmp_url", ...],
    "_all_urls": {"文件名": "tmp_url", ...}
  }

示例:
  python get_bitable_urls.py cli_a851f4d520a8900b ***FEISHU_SECRET*** \
    HeYWbu1Ppa2MEWs9AjJc09WJnce tblEsoWpihj5JwM3 recvnJQRxyUvTz

依赖: 仅 Python 标准库（urllib, json, time, os, sys）
"""

import urllib.request
import urllib.parse
import json
import time
import os
import sys


def get_token(app_id: str, app_secret: str) -> str:
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


def get_fields(token: str, app_token: str, table_id: str) -> dict:
    """返回 {field_name: type}"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read())
    return {f["field_name"]: f["type"] for f in result.get("data", {}).get("items", [])}


def get_records(token: str, app_token: str, table_id: str) -> list:
    url = (f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}"
           f"/records?page_size=100&field_names=true")
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read())
    return result.get("data", {}).get("items", [])


def get_record(token: str, app_token: str, table_id: str, record_id: str) -> dict:
    url = (f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}"
           f"/records/{record_id}?field_names=true")
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read())
    return result.get("data", {}).get("record", {})


def get_tmp_url(token: str, file_token: str) -> str | None:
    """获取单个 file_token 的 tmp_download_url（必须逐个请求）"""
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
    ".jpg": "图片", ".jpeg": "图片", ".png": "图片", ".gif": "图片", ".webp": "图片", ".bmp": "图片",
    ".mp3": "音频", ".wav": "音频", ".aac": "音频", ".m4a": "音频", ".flac": "音频", ".ogg": "音频",
    ".mp4": "视频", ".mov": "视频", ".avi": "视频", ".mkv": "视频", ".webm": "视频",
}


def classify(name: str) -> str | None:
    return _EXT.get(os.path.splitext(name)[1].lower())


def process_record(token: str, app_token: str, table_id: str, record_id: str) -> dict:
    """处理一条记录，返回结构化 JSON"""
    name_to_type = get_fields(token, app_token, table_id)
    record = get_record(token, app_token, table_id, record_id)
    fields = record.get("fields", {})
    result = {"图片": [], "音频": [], "视频": [], "_all_urls": {}}

    for field_name, field_value in fields.items():
        if field_value is None or not isinstance(field_value, list):
            continue
        # 只处理附件字段（type=17）
        if name_to_type.get(field_name) != 17:
            continue
        for item in field_value:
            if not isinstance(item, dict):
                continue
            file_token = item.get("file_token")
            name = item.get("name", file_token or "")
            if not file_token:
                continue
            tmp_url = get_tmp_url(token, file_token)
            time.sleep(0.2)  # 避免频率限制
            if tmp_url:
                result["_all_urls"][name] = tmp_url
                cat = classify(name)
                if cat:
                    result[cat].append(f"{name}||{tmp_url}")

    return result


def main():
    if len(sys.argv) < 5:
        print(json.dumps({
            "error": "用法: python get_bitable_urls.py <app_id> <app_secret> <app_token> <table_id> [record_id]"
        }, ensure_ascii=False), file=sys.stderr)
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
            for k in ("图片", "音频", "视频"):
                merged[k].extend(r[k])
            merged["_all_urls"].update(r["_all_urls"])
        print(json.dumps(merged, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()