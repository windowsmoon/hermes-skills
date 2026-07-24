#!/usr/bin/env python3
"""
buyin-harvester / scripts/feishu_writer.py
飞书多维表格创建 + 批量写入

功能:
  1. get_tenant_token() - 获取 tenant_access_token
  2. create_bitable(name) - 创建多维表格
  3. ensure_fields(token, app_token, table_id, field_names) - 确保字段存在
  4. batch_write_records(token, app_token, table_id, records) - 批量写入
  5. run() - 完整流程一键执行

配置:
  APP_ID / APP_SECRET 在脚本顶部常量中
"""

import json
import time
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError

# ═══ 飞书配置 ═══════════════════════════════════════
APP_ID     = "cli_a851f4d520a8900b"
APP_SECRET = "***"

# ═══ 字段模板 ═══════════════════════════════════════
FIELD_DEFINITIONS = [
    ("视频标题与标签", 1),
    ("博主名称",        1),
    ("发布时间",        1),
    ("视频时长",        1),
    ("视频摘要",        1),
    ("总播放量",        1),
    ("新增播放量",      1),
    ("已选类目结算金额", 1),
    ("总点赞量",        1),
]

DEFAULT_TABLE_NAME = "巨量百应爆款视频"


def _request(method, url, data=None, token=None, timeout=20):
    """通用HTTP请求"""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    req = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        body = e.read().decode()
        return {"code": -1, "msg": f"HTTP {e.code}: {body}"}
    except Exception as e:
        return {"code": -1, "msg": str(e)}


def get_tenant_token() -> str:
    """获取飞书 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = {"app_id": APP_ID, "app_secret": APP_SECRET}
    result = _request("POST", url, data)
    if result.get("code") != 0:
        raise RuntimeError(f"获取token失败: {result.get('msg')}")
    return result["tenant_access_token"]


def create_bitable(token: str, name: str = None) -> dict:
    """创建多维表格，返回 {app_token, default_table_id, url}"""
    if name is None:
        from datetime import datetime
        name = f"巨量百应爆款视频 {datetime.now().strftime('%Y-%m-%d')}"
    url = "https://open.feishu.cn/open-apis/bitable/v1/apps"
    result = _request("POST", url, {"name": name}, token)
    if result.get("code") != 0:
        raise RuntimeError(f"创建多维表格失败: {result.get('msg')}")
    app = result["data"]["app"]
    return {
        "app_token": app["app_token"],
        "table_id": app["default_table_id"],
        "url": app["url"],
        "name": app["name"],
    }


def get_field_names(token: str, app_token: str, table_id: str) -> dict:
    """获取现有字段名→field_id映射"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
    result = _request("GET", url, token=token)
    if result.get("code") != 0:
        return {}
    return {f["field_name"]: f["field_id"] for f in result["data"]["items"]}


def ensure_fields(token, app_token, table_id, field_defs=None):
    """确保表格包含指定字段，缺失的自动添加"""
    if field_defs is None:
        field_defs = FIELD_DEFINITIONS
    existing = get_field_names(token, app_token, table_id)
    # 删除默认字段
    for fname in ["文本", "单选", "日期", "附件"]:
        if fname in existing:
            fid = existing[fname]
            _request("DELETE",
                f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields/{fid}",
                token=token)
            time.sleep(0.1)
            del existing[fname]
    # 添加缺失字段
    for fname, ftype in field_defs:
        if fname not in existing:
            url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
            result = _request("POST", url, {"field_name": fname, "type": ftype}, token)
            if result.get("code") == 0:
                existing[fname] = result["data"]["field"]["field_id"]
                print(f"  ✅ 字段 '{fname}' 已添加")
            else:
                print(f"  ⚠️ 字段 '{fname}' 添加失败: {result.get('msg')}")
            time.sleep(0.3)
    return existing


def clear_table_records(token, app_token, table_id):
    """清空表格所有记录"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
    result = _request("GET", url, token=token)
    if result.get("code") != 0:
        return
    items = result.get("data", {}).get("items", [])
    for item in items:
        rid = item["record_id"]
        _request("DELETE",
            f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{rid}",
            token=token)
        time.sleep(0.1)


def batch_write_records(token, app_token, table_id, records):
    """批量写入记录到飞书多维表格"""
    if not records:
        return {"code": 0, "count": 0, "record_ids": []}
    formatted = [{"fields": {k: str(v) for k, v in r.items()}} for r in records]
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create"
    result = _request("POST", url, {"records": formatted}, token, timeout=30)
    if result.get("code") == 0:
        created = result["data"]["records"]
        return {"code": 0, "count": len(created), "record_ids": [r["record_id"] for r in created]}
    return result


def append_records(token, app_token, table_id, records):
    """追加写入（单条逐写）"""
    if not records:
        return {"code": 0, "count": 0, "record_ids": []}
    ids = []
    for r in records:
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        result = _request("POST", url, {"fields": {k: str(v) for k, v in r.items()}}, token)
        if result.get("code") == 0:
            ids.append(result["data"]["record"]["record_id"])
        time.sleep(0.3)
    return {"code": 0, "count": len(ids), "record_ids": ids}


def run():
    """CLI入口：完整流程"""
    import argparse
    parser = argparse.ArgumentParser(description="巨量百应采集 → 飞书多维表格")
    parser.add_argument("--name", default=DEFAULT_TABLE_NAME)
    parser.add_argument("--records-json")
    parser.add_argument("--app-token")
    parser.add_argument("--table-id")
    parser.add_argument("--append", action="store_true")
    args = parser.parse_args()

    print("🔑 获取Token...")
    token = get_tenant_token()
    print(f"  ✅ Token: {token[:20]}...")

    if args.app_token and args.table_id:
        app_token, table_id = args.app_token, args.table_id
        print(f"📋 使用已有表格: {app_token}")
    else:
        print(f"📦 创建多维表格: {args.name}")
        table = create_bitable(token, args.name)
        app_token, table_id = table["app_token"], table["table_id"]
        print(f"  ✅ app_token: {app_token}")
        print(f"  ✅ table_id: {table_id}")
        print(f"  🔗 {table['url']}")

    print("📝 设置字段...")
    ensure_fields(token, app_token, table_id)

    if not args.append and not args.records_json:
        print("🧹 清空已有记录...")
        clear_table_records(token, app_token, table_id)

    if args.records_json:
        with open(args.records_json, encoding='utf-8') as f:
            records = json.load(f)
        if args.append:
            print(f"📥 逐条追加 {len(records)} 条...")
            result = append_records(token, app_token, table_id, records)
        else:
            print(f"📥 批量写入 {len(records)} 条...")
            result = batch_write_records(token, app_token, table_id, records)
        if result.get("code") == 0:
            print(f"  ✅ 成功写入 {result['count']} 条")
        else:
            print(f"  ❌ 写入失败: {result.get('msg')}")

    base_url = f"https://swi2cdl2nbg.feishu.cn/base/{app_token}"
    print(f"\n🔗 {base_url}")
    print(f"  app_token: {app_token}")
    print(f"  table_id: {table_id}")


if __name__ == '__main__':
    run()
