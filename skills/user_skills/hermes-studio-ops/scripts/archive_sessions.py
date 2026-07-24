"""
archive_sessions.py  三信号监控版
同时监控：
  1. WAL 文件大小变化
  2. DB 文件 mtime 变化
  3. WAL size 骤降（checkpoint 刚发生）

使用 Hermes 捆绑的 Python 运行：
  "C:\\Users\\Admin\\.hermes-web-ui\\desktop-runtime\\hermes\\0.18.0\\win-x64\\python\\python.exe" "D:\\Program\\Hermes Studio\\relate program\\archive_sessions.py"

注意：运行时必须使用 Hermes 捆绑的 Python（用户本机可能无 Python）。
"""

import sqlite3, json, time, sys, os, re
from pathlib import Path
from datetime import datetime

# ── 配置（绝对路径，不依赖环境变量）───────────────────────
HERMES_DIR  = Path("C:/Users/Admin/AppData/Local/hermes")
WEB_UI_DIR  = Path("C:/Users/Admin/.hermes-web-ui")
DB_PATH     = WEB_UI_DIR / "hermes-web-ui.db"
WAL_PATH    = WEB_UI_DIR / "hermes-web-ui.db-wal"
OUT_DIR     = Path("D:/hermes-data/conversation")
PROFILE     = os.environ.get("HERMES_PROFILE", "default")

# ── 数据库工具 ──────────────────────────────────────────────
def safe_name(title, sid):
    name = (title or sid).strip()
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', name)
    return name[:200] or sid

def get_columns(conn, table):
    sql = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
        (table,)
    ).fetchone()[0]
    return re.findall(r'"(\w+)"', sql)[1:]   # 跳过表名 token

def handle_archives(conn, sess_cols, msg_cols, processed):
    cur = conn.execute(
        "SELECT id, title FROM sessions WHERE is_archived = 1 AND profile = ?", (PROFILE,)
    )
    for sid, title in cur.fetchall():
        if sid in processed:
            continue
        processed.add(sid)
        ts = datetime.now().strftime('%H:%M:%S')
        print(f"[{ts}] 归档操作: {title or sid}")
        try:
            msgs = [dict(zip(msg_cols, row))
                    for row in conn.execute(
                        "SELECT * FROM messages WHERE session_id = ? ORDER BY timestamp", (sid,)
                    ).fetchall()]
            s = dict(zip(sess_cols,
                         conn.execute("SELECT * FROM sessions WHERE id = ?", (sid,)).fetchone()))
            data = {
                "_meta": {"exported_at": datetime.now().isoformat(), "source": str(DB_PATH)},
                "session": s,
                "messages": msgs,
            }
            base = safe_name(title or s.get('title'), sid)
            path = OUT_DIR / f"{base}.json"
            i = 1
            while path.exists():
                path = OUT_DIR / f"{base}_{i}.json"
                i += 1
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"[{ts}]   已保存: {path.name}")
        except Exception as e:
            print(f"[{ts}]   失败: {e}")

# ── Hermes 进程检测（延迟导入，30 秒间隔） ─────────────────
_hermes_pid = None
_last_check = 0
_HERMES_CHECK_INTERVAL = 30

def is_hermes_alive():
    global _hermes_pid, _last_check
    now = time.time()
    if now - _last_check < _HERMES_CHECK_INTERVAL:
        return _hermes_pid is not None
    _last_check = now
    import psutil
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            cl = ' '.join(str(c) for c in (proc.info.get('cmdline') or [])).lower()
            if 'gateway' in cl and 'hermes' in cl:
                _hermes_pid = proc.info['pid']
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    _hermes_pid = None
    return False

# ── 主程序 ────────────────────────────────────────────────
def main():
    print("=" * 54)
    print("  Hermes 归档会话监控")
    print("  Hermes 关闭 -> 自动停止")
    print("=" * 54 + "\n")
    sys.stdout.flush()

    if not DB_PATH.exists():
        print(f"ERROR: 数据库不存在: {DB_PATH}")
        sys.exit(1)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH), timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    sess_cols = get_columns(conn, "sessions")
    msg_cols  = get_columns(conn, "messages")

    print(f"DB:  {DB_PATH}")
    print(f"OUT: {OUT_DIR}\n")
    sys.stdout.flush()

    # 幂等：跳过已导出文件
    processed = set()
    for f in OUT_DIR.glob("*.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            sid = d.get("session", {}).get("id")
            if sid:
                processed.add(sid)
        except Exception:
            pass
    print(f"已有 {len(processed)} 个会话已导出")

    # 初始化状态
    last_wal = 0
    last_db_mtime = 0
    prev_wal = 0
    try:
        last_wal = WAL_PATH.stat().st_size
        last_db_mtime = DB_PATH.stat().st_mtime
    except FileNotFoundError:
        pass

    print(f"初始: WAL={last_wal}B, DB_mtime={last_db_mtime}")
    print("等待归档操作...\n")
    sys.stdout.flush()

    try:
        while True:
            if not is_hermes_alive():
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Hermes 未运行，停止。")
                break

            try:
                wal_size = WAL_PATH.stat().st_size
            except FileNotFoundError:
                wal_size = 0

            db_mtime = DB_PATH.stat().st_mtime

            # 三个触发条件（见 hermes-studio-ops skill 的触发机制说明）
            wal_changed = wal_size != last_wal
            db_changed = db_mtime != last_db_mtime
            checkpoint_happened = (prev_wal > 0 and wal_size < prev_wal * 0.5)

            if wal_changed or db_changed or checkpoint_happened:
                if checkpoint_happened:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 检测到 checkpoint")
                last_wal = wal_size
                last_db_mtime = db_mtime
                # 强制 checkpoint 确保读到最新数据
                try:
                    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                except Exception:
                    pass
                handle_archives(conn, sess_cols, msg_cols, processed)

            prev_wal = wal_size
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n手动停止。")
    finally:
        conn.close()

if __name__ == "__main__":
    main()