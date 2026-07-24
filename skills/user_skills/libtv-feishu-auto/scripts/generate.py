#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LibTV × 飞书多维表格自动化生成脚本
独立运行，不依赖 libtv-cli skill / feishu-cli skill
"""

import os
import sys
import json
import time
import uuid
import subprocess
import tempfile
import shutil
import urllib.request
import urllib.error
import urllib.parse

# ──────────────────────────────────────────────
# 1. 飞书配置
# ──────────────────────────────────────────────
FEISHU_APP_ID     = "cli_a851f4d520a8900b"
FEISHU_APP_SECRET = "***FEISHU_SECRET***"
FEISHU_BASE_URL   = "https://open.feishu.cn/open-apis"
BITABLE_APP_TOKEN = "HeYWbu1Ppa2MEWs9AjJc09WJnce"
BITABLE_TABLE_ID  = "tblEsoWpihj5JwM3"

# field_id → 参数名
FIELD_IDS = {
    "task_type":       "fldzssggPC",   # 任务性质
    "status":          "fldvehN4ht",   # 状态
    "description":     "fldSlaBSHs",   # 分镜描述
    "image":           "fldzAmcI8V",   # 图片（附件）
    "audio":           "fldqpoEqj1",   # 音频（附件）
    "prompt":          "fldnm6sn3A",   # 提示词
    "img_model":       "fld7buiPcx",   # 图片_model
    "img_ratio":       "fldvNQi32k",   # 图片_ratio
    "img_resolution":  "fldOWhQeSj",   # 图片_resolution
    "img_quality":     "fldwYMwyYU",   # 图片_quality
    "img_modeType":    "fld2VXwLWQ",   # 图片_modeType
    "vid_model":       "fldn8xdnz7",   # 视频_model
    "vid_ratio":       "fldPnNN6jb",   # 视频_ratio
    "vid_resolution":  "fldgXVZc6v",   # 视频_resolution
    "vid_modeType":    "fldBdrUtnJ",   # 视频_modeType
    "vid_duration":    "fldDyGaR3b",   # 视频_duration
    "vid_enableSound": "fldmPLLBiV",   # 视频_enableSound
    "vid_search_enabled": "flduOFgVdL",# 视频_search_enabled
    "result_image":    "fldbzYitha",   # 图片URL
    "result_video":    "fldr2UU4YN",   # 视频（附件）
    "result_video_url":"fld6GP1N8t",   # 视频URL
}

# 任务性质 name → task_key
TASK_NAME_MAP = {
    "生成分镜脚本": "skip",
    "生成背景图":   "background",
    "生成角色卡":   "character",
    "生成道具组图": "prop_set",
    "生成分镜图":   "storyboard",
    "生成视频片段": "video",
}

# 任务性质 option_id → task_key（备用精确匹配）
TASK_OPT_MAP = {
    "optXZG6nXo": "skip",      # 生成分镜脚本
    "optgFtikil": "background", # 生成背景图
    "opt6qLdILp": "character",  # 生成角色卡
    "optxxwRXpb": "prop_set",  # 生成道具组图
    "optGpFy8HB": "storyboard",# 生成分镜图
    "optjj0PnHT": "video",     # 生成视频片段
}

# 状态字段值（中文文本，option_id 已从多维表格删除）
STATUS = {
    "pending": "待处理",
    "running": "进行中",
    "done":    "完成",
    "failed":  "失败",
}

# 模型 modelKey → modelName（LibTV --set 只接受 modelName）
MODEL_NAME_MAP = {
    # 图片模型
    "Lib Image":    "lib-image-2",
    "Lib Navo 2":   "nebula-2-flash",
    "Lib Navo Pro":  "nebula-ultra",
    # 视频模型
    "Seedance 2.0 VIP":     "star-video2",
    "Seedance 2.0 Fast VIP": "star-video2-fast",
    "Seedance 2.0 Mini":    "star-video2-mini",
}

# 任务默认参数（可被飞书字段值覆盖）
TASK_DEFAULTS = {
    "background": dict(model="Lib Navo 2",  modeType="text2image",
                       img_ratio="16:9",     img_quality="2K"),
    "prop_set":   dict(model="Lib Navo 2",  modeType="text2image",
                       img_ratio="16:9",     img_quality="2K"),
    "character":  dict(model="Lib Image",   modeType="image2image",
                       img_ratio="auto",    img_resolution="2K"),
    "storyboard": dict(model="Lib Image",   modeType="image2image",
                       img_ratio="auto",    img_resolution="2K"),
    "video":      dict(model="Seedance 2.0 Mini", modeType="mixed2video",
                       vid_ratio="16:9",    vid_resolution="720p",
                       vid_duration=5,      vid_enableSound="on",
                       vid_search_enabled="1"),
}

# ──────────────────────────────────────────────
# 2. HTTP 基础请求
# ──────────────────────────────────────────────
def api_req(method, path, token=None, body=None, params=None):
    url = FEISHU_BASE_URL + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body is not None else None
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}" if token else "",
    }
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode() if e.fp else ""
        raise RuntimeError(f"HTTP {e.code} {method} {path}: {body_text}") from e

def get_token():
    result = api_req("POST", "/auth/v3/tenant_access_token/internal",
                     body={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET})
    if result.get("code") != 0:
        raise RuntimeError(f"获取飞书 token 失败: {result}")
    return result["tenant_access_token"]

# ──────────────────────────────────────────────
# 3. 飞书多维表格操作
# ──────────────────────────────────────────────
def list_all_task_records(token):
    """
    遍历所有记录，遇到任务性质为空时停止。
    只收集状态 != 完成 的待处理/失败记录。
    已完成的记录直接跳过（不处理）。
    """
    records = []
    page_token = None
    while True:
        params = {"page_token": page_token} if page_token else {}
        result = api_req(
            "GET",
            f"/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{BITABLE_TABLE_ID}/records",
            token=token, params=params,
        )
        for item in result["data"]["items"]:
            fields = item.get("fields", {})

            # 解析任务性质
            task_val = fields.get("任务性质", {})
            if isinstance(task_val, dict):
                task_name = task_val.get("text", "") or task_val.get("name", "")
            else:
                task_name = str(task_val) if task_val else ""

            # 任务性质为空 → 停止遍历
            if not task_name:
                break

            # 解析状态（返回中文文本：待处理/进行中/完成/失败）
            status_val = fields.get("状态", {})
            if isinstance(status_val, dict):
                status_name = status_val.get("name", "") or status_val.get("text", "") or ""
            else:
                status_name = str(status_val).strip() if status_val else ""

            # 状态 = 完成 → 跳过该行，继续下一条
            if status_name == STATUS["done"]:
                print(f"  [跳过] record_id={item['record_id']} 状态=已完成")
                continue

            # 待处理/进行中/失败 → 加入待处理列表
            records.append({"record_id": item["record_id"], "fields": fields, "task_name": task_name})

        if not result["data"].get("has_more"):
            break
        page_token = result["data"]["page_token"]
        # 如果最后一条任务性质为空，停止
        if records and not records[-1]["task_name"]:
            records.pop()
            break
    return records

def update_record(token, record_id, fields):
    """更新记录字段（写入结果）"""
    result = api_req(
        "PUT",
        f"/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{BITABLE_TABLE_ID}/records/{record_id}",
        token=token,
        body={"fields": fields},
    )
    if result.get("code") != 0:
        raise RuntimeError(f"更新记录失败: {result}")
    return result

def get_attachment_urls_from_tokens(token, file_tokens):
    """
    批量获取附件下载链接（备用，当附件对象没有 url 时使用）。
    file_tokens: list[str] of file_token
    """
    if not file_tokens:
        return []
    result = api_req(
        "POST",
        "/drive/v1/medias/batch_get_tmp_download_url",
        token=token,
        body={"file_tokens": file_tokens},
    )
    return result.get("data", {}).get("items", [])

# ──────────────────────────────────────────────
# 4. 字段值读取工具
# ──────────────────────────────────────────────
def read_text_field(fields, key, default=""):
    """读取文本字段，处理富文本格式"""
    val = fields.get(key, default)
    if isinstance(val, dict):
        return val.get("text", "") or val.get("name", "") or default
    return str(val) if val else default

def read_attachment_field(fields, key):
    """
    读取附件字段，返回 {url, name} 列表。
    飞书记录 API 返回的附件对象已含 download url：
    {"file_token": "xxx", "name": "xxx", "url": "https://open.feishu.cn/.../download"}
    """
    val = fields.get(key, [])
    if not val:
        return []
    if isinstance(val, list):
        result = []
        for f in val:
            if isinstance(f, dict):
                url = f.get("url") or f.get("download_url") or ""
                name = f.get("name", "file")
                if url:
                    result.append({"url": url, "name": name})
        return result
    return []

def read_select_field(fields, key):
    """读取单选字段，返回选项名"""
    val = fields.get(key, {})
    if isinstance(val, dict):
        return val.get("text", "") or val.get("name", "") or ""
    return str(val) if val else ""

def read_number_field(fields, key, default=None):
    """读取数字字段"""
    val = fields.get(key)
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

# ──────────────────────────────────────────────
# 5. LibTV CLI 封装
# ──────────────────────────────────────────────
LIBTV_CLI  = os.path.expanduser(r"~\.libtv\libtv.exe")
LIBTV_PROJ = "a412891277714b22b8f902e948c4af4a"

def libtv(args, timeout=600, cwd=None):
    """运行 libtv 命令，返回 (returncode, stdout, stderr)"""
    cmd = [LIBTV_CLI] + args
    env = os.environ.copy()
    env["PATH"] = os.path.dirname(LIBTV_CLI) + os.pathsep + env.get("PATH", "")
    kwargs = dict(
        capture_output=True, text=True, env=env,
        timeout=timeout,
        cwd=cwd or os.getcwd(),
    )
    print(f"    [libtv] {' '.join(args[:3])}...")
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        print(f"    [libtv] FAIL rc={result.returncode}")
        print(f"    [libtv] stderr: {result.stderr[:300]}")
    else:
        print(f"    [libtv] OK")
    return result.returncode, result.stdout, result.stderr

def libtv_ensure_project():
    libtv(["project", "use", LIBTV_PROJ])

def libtv_upload(name, file_path, node_type):
    """上传本地文件为 LibTV 资源节点，返回 nodeKey 或 None"""
    rc, stdout, stderr = libtv(
        ["upload", name, "-f", file_path, "-t", node_type, "-p", LIBTV_PROJ],
        timeout=120,
    )
    if rc != 0:
        return None
    # 解析 nodeKey：stdout 可能是多行 JSON，整段解析取 nodeKey
    try:
        data = json.loads(stdout.strip())
        return data.get("nodeKey") or (data.get("node") or {}).get("nodeKey")
    except Exception:
        pass
    return None

def libtv_create_and_run(node_name, node_type, prompt, params, left_nodes=None):
    """
    两步生成：先建节点，再 --run 触发并等待结果。
    返回生成结果 URL 或 None。
    
    注意：libtv node create --run 会在节点创建后立即返回，
    不等生成完成。所以必须分两步：
    1. libtv node create <name>（不带 --run）
    2. libtv node <name> --run（触发生成并等待完成，输出含 url）
    """
    # Step 1: 建节点 + 连线（不带 --run）
    create_args = [
        "node", "create", node_name,
        "-t", node_type,
        "-p", LIBTV_PROJ,
        "--prompt", prompt,
    ]
    for key, val in params.items():
        if val is None:
            continue
        if isinstance(val, bool):
            val = "true" if val else "false"
        if " " in str(val):
            val = f'"{val}"'
        create_args += ["-s", f"{key}={val}"]
    if left_nodes:
        for n in left_nodes:
            create_args += ["--left", n]

    rc, stdout, stderr = libtv(create_args, timeout=60)
    if rc != 0:
        raise RuntimeError(f"libtv node create 失败: {stderr[:200]}")

    # 从 stdout 解析 nodeKey（用于后续 --run）
    node_key = None
    try:
        data = json.loads(stdout.strip())
        node_key = data.get("newNodeKey") or data.get("node", {}).get("nodeKey")
    except Exception:
        pass
    if not node_key:
        raise RuntimeError(f"无法从 create 输出解析 nodeKey: {stdout[:200]}")

    # Step 2: 触发生成并等待（--run）
    # 用 newNodeKey 作为节点标识（更精确）
    run_args = ["node", node_key, "-p", LIBTV_PROJ, "--run"]
    rc, stdout, stderr = libtv(run_args, timeout=600)
    if rc != 0:
        raise RuntimeError(f"libtv node --run 失败: {stderr[:200]}")

    # 从 stdout 解析结果 URL（终态 JSON）
    # stdout 可能是多行格式化 JSON，需去掉换行后整体解析
    compact = ''.join(stdout.split())
    try:
        data = json.loads(compact)
        # 视频：data.url 是数组
        url = data.get("data", {}).get("url")
        if isinstance(url, list) and url:
            return url[0]
        if url:
            return url
        # 图片：data.url
        node_data = data.get("node", {}) or data
        url2 = node_data.get("data", {}).get("url")
        if isinstance(url2, list) and url2:
            return url2[0]
        if url2:
            return url2
    except Exception as e:
        pass
    return None

# ──────────────────────────────────────────────
# 6. 图片生成（通用）
# ──────────────────────────────────────────────
def generate_image(token, record_id, fields, task_key, defaults, counter):
    """
    执行图片生成任务
    - task_key: background / prop_set / character / storyboard
    - defaults: TASK_DEFAULTS[task_key]
    """
    print(f"\n  [图片生成] task={task_key}")

    # 读取 prompt（优先 提示词，其次 分镜描述）
    prompt = read_text_field(fields, "提示词") or read_text_field(fields, "分镜描述")
    if not prompt:
        raise ValueError("提示词和分镜描述均为空，无法生成图片")

    # 读取模型（飞书字段优先，否则用默认）
    model = read_select_field(fields, "图片_model") or defaults["model"]
    if task_key in ("background", "prop_set") and model not in ("Lib Navo 2", "Lib Navo Pro"):
        print(f"  [警告] 任务性质要求 Lib Navo 2/Pro，实际: {model}，强制使用 Lib Navo 2")
        model = "Lib Navo 2"

    # 读取 modeType
    mode_type = read_select_field(fields, "图片_modeType") or defaults.get("modeType", "image2image")

    # 读取图片附件（参考图，image2image 需要）
    img_attachments = read_attachment_field(fields, "图片")
    local_img_paths = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for item in img_attachments:
            dl_url = item.get("url", "")
            fname = item.get("name", "ref_" + str(uuid.uuid4())[:8])
            if not dl_url:
                continue
            local_path = os.path.join(tmpdir, fname)
            # 飞书 download URL 需要 Bearer token 认证
            download_req = urllib.request.Request(dl_url, headers={"Authorization": f"Bearer {token}"})
            with urllib.request.urlopen(download_req, timeout=60) as resp:
                with open(local_path, "wb") as out_f:
                    shutil.copyfileobj(resp, out_f)
            local_img_paths.append((fname, local_path))

        # 上传参考图作为资源节点
        resource_nodes = []
        resource_node_keys = []
        for i, (fname, fpath) in enumerate(local_img_paths):
            # 用 record_id 前缀保证唯一，同一记录多次运行也不会冲突
            node_name = f"REF-{record_id[:8]}-{task_key}-{i+1}"
            nk = libtv_upload(node_name, fpath, "image")
            if nk:
                resource_nodes.append(node_name)
                resource_node_keys.append(nk)
                print(f"    参考图 {i+1}: {node_name} (nodeKey={nk})")

        # 构建参数
        params = {"model": model, "modeType": mode_type}

        # ratio
        ratio = read_select_field(fields, "图片_ratio") or defaults.get("img_ratio", "auto")
        if ratio:
            params["ratio"] = ratio

        # resolution / quality（按模型区分）
        res = read_select_field(fields, "图片_resolution")
        qual = read_select_field(fields, "图片_quality")
        if model == "Lib Image":
            params["resolution"] = res or defaults.get("img_resolution", "2K")
            if qual:
                params["quality"] = qual
        else:  # Navo 系列用 quality 字段
            params["quality"] = qual or defaults.get("img_quality", "2K")

        node_name = f"图片-{task_key}-{record_id[:8]}"
        # 资源节点用 nodeKey 连线，不用显示名（同名节点多，名字会匹配到空的）
        lefts = resource_node_keys if resource_node_keys else None

        # 同 record_id 复用同名节点（同名已存在则更新参数再运行，覆盖旧结果）
        try:
            result_url = libtv_create_and_run(node_name, "image", prompt, params, lefts)
        except RuntimeError as e:
            err = str(e)
            if "已存在" in err or "exists" in err.lower():
                print(f"    节点已存在，直接删除后重新创建...")
                # 删除旧节点（保证干净状态）
                libtv(["node", "delete", node_name, "-p", LIBTV_PROJ], timeout=30)
                # 重新创建
                result_url = libtv_create_and_run(node_name, "image", prompt, params, lefts)
        print(f"    生成结果: {result_url}")

        # 写回飞书
        if result_url:
            update_record(token, record_id, {"图片URL": result_url, "状态": STATUS["done"]})

        return result_url

# ──────────────────────────────────────────────
# 7. 视频生成
# ──────────────────────────────────────────────
def generate_video(token, record_id, task_key, fields, defaults, counter):
    """
    执行视频生成任务
    """
    print(f"\n  [视频生成] modeType=mixed2video")

    # 读取 prompt（优先 分镜描述，其次 提示词）
    prompt = read_text_field(fields, "分镜描述") or read_text_field(fields, "提示词")
    if not prompt:
        raise ValueError("分镜描述和提示词均为空，无法生成视频")

    # 读取模型
    model = read_select_field(fields, "视频_model") or defaults["model"]

    # 上传图片和音频附件
    img_attachments = read_attachment_field(fields, "图片")
    aud_attachments = read_attachment_field(fields, "音频")
    # 附件已在 read_attachment_field 中解析出 url，直接用
    img_attachments = read_attachment_field(fields, "图片")
    aud_attachments = read_attachment_field(fields, "音频")
    all_attachments = img_attachments + aud_attachments

    resource_nodes = []
    resource_node_keys = []
    lefts = None
    with tempfile.TemporaryDirectory() as tmpdir:
        for idx, item in enumerate(all_attachments):
            dl_url = item.get("url", "")
            fname = item.get("name", "res_" + str(uuid.uuid4())[:8])
            if not dl_url:
                continue
            local_path = os.path.join(tmpdir, fname)
            # 飞书 download URL 需要 Bearer token 认证
            download_req = urllib.request.Request(dl_url, headers={"Authorization": f"Bearer {token}"})
            with urllib.request.urlopen(download_req, timeout=60) as resp:
                with open(local_path, "wb") as out_f:
                    shutil.copyfileobj(resp, out_f)

            # 判断类型（图片在前，音频在后）
            ntype = "image" if idx < len(img_attachments) else "audio"
            node_name = f"REFV-{record_id[:8]}-{task_key}-{'img' if ntype=='image' else 'aud'}-{idx+1}"
            nk = libtv_upload(node_name, local_path, ntype)
            if nk:
                resource_nodes.append(node_name)
                resource_node_keys.append(nk)
                lefts = resource_node_keys
                print(f"    上传 {ntype}: {node_name} (nodeKey={nk})")

        # 构建参数
        params = {
            "model":       model,
            "modeType":    "mixed2video",
            "ratio":       read_select_field(fields, "视频_ratio")      or defaults.get("vid_ratio", "16:9"),
            "resolution":  read_select_field(fields, "视频_resolution") or defaults.get("vid_resolution", "720p"),
            "duration":    read_number_field(fields, "视频_duration",    defaults.get("vid_duration", 5)),
            "enableSound": read_select_field(fields, "视频_enableSound") or defaults.get("vid_enableSound", "on"),
            "search_enabled": read_select_field(fields, "视频_search_enabled") or defaults.get("vid_search_enabled", "1"),
        }

        node_name = f"视频-{record_id[:8]}-{task_key}"
        result_url = libtv_create_and_run(node_name, "video", prompt, params, lefts)
        print(f"    生成结果: {result_url}")

        # 写回飞书
        if result_url:
            # 视频URL字段（type=15 Url）
            update_record(token, record_id, {
                "视频URL": {"link": result_url, "text": result_url},
                "状态": STATUS["done"],
            })
            # 视频附件字段（type=17）需要 file_token，无法通过 URL 直接写入，暂不处理

        return result_url

# ──────────────────────────────────────────────
# 8. 主流程
# ──────────────────────────────────────────────
def process_record(token, record_id, fields, task_name, counter):
    """处理单条记录，按任务性质分发"""
    task_key = TASK_NAME_MAP.get(task_name)
    if not task_key:
        print(f"  [跳过] 未知任务性质: {task_name}")
        return False

    if task_key == "skip":
        print(f"  [跳过] 生成分镜脚本（多维表格自动化处理）")
        return True  # 算成功，不报错

    defaults = TASK_DEFAULTS.get(task_key, {})
    error = None

    try:
        if task_key in ("background", "prop_set", "character", "storyboard"):
            # 图片生成任务
            url = generate_image(token, record_id, fields, task_key, defaults, counter)
            if url:
                print(f"  [完成] 图片已生成并写入飞书")
            else:
                raise RuntimeError("图片生成未返回结果 URL")
        elif task_key == "video":
            # 视频生成任务
            url = generate_video(token, record_id, task_key, fields, defaults, counter)
            if url:
                print(f"  [完成] 视频已生成并写入飞书")
            else:
                raise RuntimeError("视频生成未返回结果 URL")
        return True

    except Exception as e:
        print(f"  [失败] {e}")
        try:
            update_record(token, record_id, {"状态": STATUS["failed"]})
        except Exception:
            pass
        return False

def main():
    print("=" * 60)
    print("LibTV × 飞书多维表格自动化")
    print("=" * 60)

    # 初始化 LibTV 项目绑定
    print("\n[1] 初始化 LibTV 项目...")
    libtv_ensure_project()

    # 获取飞书 token
    print("\n[2] 获取飞书访问令牌...")
    token = get_token()

    # 读取所有任务性质非空的记录，直到任务性质为空停止
    print("\n[3] 读取任务记录（任务性质非空）...")
    records = list_all_task_records(token)
    print(f"  找到 {len(records)} 条任务记录")
    if not records:
        print("无任务记录，退出。")
        return

    # 逐条处理
    success, failed = 0, 0
    for i, rec in enumerate(records, 1):
        print(f"\n{'─'*50}")
        print(f"处理 {i}/{len(records)}：record_id={rec['record_id']}")
        print(f"任务性质：{rec['task_name']}")

        ok = process_record(token, rec["record_id"], rec["fields"], rec["task_name"], i)
        if ok:
            success += 1
        else:
            failed += 1

    print("\n" + "=" * 60)
    print(f"全部完成！成功 {success} 条，失败 {failed} 条")
    print("=" * 60)

if __name__ == "__main__":
    main()
