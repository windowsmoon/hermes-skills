#!/usr/bin/env python3
"""
QR 登录标准脚本 — 当终端乱码时用此脚本替代 CLI 登录。
两种模式：
  1. standalone: 生成二维码 + 等待扫码（阻塞直到扫码完成或超时）
  2. bg-qr: 只生成二维码图片 + 保存登录数据（不阻塞），适合让用户先扫码，
     后续用独立的 long-poll 进程完成登录

用法：
  uvx python qr-login-workflow.py standalone   # 阻塞式，等扫码
  uvx python qr-login-workflow.py bg-qr        # 仅生成二维码 + 保存数据
"""

import sys, json, os, time

# 1) 添加 uv tool 安装的包到 Python 路径
UV_TOOLS_SITE = os.path.expanduser(
    "~/AppData/Roaming/uv/tools/mijiaapi/Lib/site-packages"
)
sys.path.insert(0, UV_TOOLS_SITE)

from mijiaAPI import mijiaAPI
from pathlib import Path
from qrcode import QRCode

TEMP_DIR = os.path.expanduser("~/AppData/Local/Temp")
AUTH_PATH = Path.home() / ".config" / "mijia-api" / "auth.json"


def get_login_data():
    """获取米家登录数据。返回 (api, login_data) 或 (api, None) 表示已刷新。"""
    AUTH_PATH.parent.mkdir(parents=True, exist_ok=True)
    api = mijiaAPI(auth_data_path=str(AUTH_PATH))
    data = api._get_qr_login_data()
    if data.get("refreshed"):
        return api, None
    return api, data


def save_qr_image(login_url: str, output_path: str):
    """从 loginUrl 本地生成二维码 PNG 图片。"""
    qr = QRCode(border=2, box_size=10)
    qr.add_data(login_url)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)


def save_login_data(api, data: dict):
    """保存完整登录数据供后续 long-poll 使用。"""
    info_path = os.path.join(TEMP_DIR, "mijia_login_data.json")
    with open(info_path, "w") as f:
        json.dump(data, f)
    return info_path


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "standalone"

    api, data = get_login_data()
    if data is None:
        print("TOKEN_REFRESHED — 认证已有效，无需登录")
        return

    login_url = data.get("loginUrl", "")
    if not login_url:
        print("ERROR: 未获取到 loginUrl")
        sys.exit(1)

    # 生成二维码图片
    img_path = os.path.join(TEMP_DIR, "mijia_qr_login.png")
    save_qr_image(login_url, img_path)
    print(f"QR_IMAGE: {img_path} ({os.path.getsize(img_path)} bytes)")

    if mode == "bg-qr":
        # 保存数据 + 退出
        save_login_data(api, data)
        print("MODE_BG — 登录数据已保存，可稍后运行 long-poll 完成登录")
        print(f"LOGIN_URL: {login_url}")
        return

    # standalone 模式：直接等待扫码
    print("等待扫码...")
    sys.stdout.flush()
    result = api._complete_qr_login(data)
    print("LOGIN_SUCCESS")


if __name__ == "__main__":
    main()