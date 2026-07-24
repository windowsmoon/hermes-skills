#!/usr/bin/env python3
"""
Hermes Email Session Fork Monitor
Monitors hermes-web-ui.db for new email source sessions.
Forks them into CLI sessions with structured summary + attachment info.
"""
import sqlite3
import json
import time
import re
import uuid
import logging
import sys
from pathlib import Path

# Config
DB_PATH = Path.home() / ".hermes-web-ui" / "hermes-web-ui.db"
STATE_DIR = Path.home() / "AppData" / "Local" / "hermes"
STATE_FILE = STATE_DIR / "fork_state.json"
POLL_INTERVAL = 5
LOG_FILE = STATE_DIR / "fork_monitor.log"

FORK_SOURCES = {"email"}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(str(LOG_FILE), encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("email_fork")

def load_state():
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            return set(data.get("forked", []))
        except (json.JSONDecodeError, KeyError):
            return set()
    return set()

def save_state(forked_ids):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(
        json.dumps({"forked": list(forked_ids)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

def get_columns(conn, table):
    sql = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone()[0]
    return re.findall(r'"(\w+)"', sql)[1:]

def get_messages(conn, session_id):
    msg_cols = get_columns(conn, "messages")
    col_str = ", ".join('"{}"'.format(c) for c in msg_cols)
    rows = conn.execute(
        "SELECT {} FROM messages WHERE session_id=? ORDER BY timestamp ASC".format(col_str),
        (session_id,)
    ).fetchall()
    return [dict(zip(msg_cols, r)) for r in rows]

def find_new_platform_sessions(conn, forked_ids):
    sess_cols = get_columns(conn, "sessions")
    col_str = ", ".join('"{}"'.format(c) for c in sess_cols)
    conditions = " OR ".join("source='{}'".format(s) for s in FORK_SOURCES)
    rows = conn.execute(
        "SELECT {} FROM sessions WHERE ({}) ORDER BY last_active ASC".format(col_str, conditions)
    ).fetchall()
    news = []
    for r in rows:
        sess = dict(zip(sess_cols, r))
        if sess["id"] not in forked_ids:
            news.append(sess)
    return news

def parse_email(content):
    result = {"subject": "", "sender": "", "time": "", "body": "", "attachments": []}
    text = str(content)
    m = re.search(r'\*\*邮件主题\*\*:\s*(.*)', text)
    if m: result["subject"] = m.group(1).strip()
    m = re.search(r'\*\*发件人\*\*:\s*(.*)', text)
    if m: result["sender"] = m.group(1).strip()
    m = re.search(r'\*\*时间\*\*:\s*(.*)', text)
    if m: result["time"] = m.group(1).strip()
    m = re.search(r'\*\*邮件正文\*\*:\s*(.*?)(?:APPROVE_|REJECT_|---)', text, re.DOTALL)
    if m:
        body = m.group(1).strip()
        body = re.sub(r'\r\n', '\n', body)
        body = re.sub(r'\n{3,}', '\n\n', body)
        result["body"] = body.strip()
    else:
        result["body"] = text[:500]
    for m in re.finditer(r'附件[：:]\s*(.+)', text):
        fname = m.group(1).strip()
        if fname and fname not in result["attachments"]:
            result["attachments"].append(fname)
    return result

def build_summary(parsed):
    lines = []
    lines.append("## \U0001f4ec \u90ae\u4ef6\u6458\u8981")
    lines.append("")
    if parsed["subject"]:
        lines.append("**\u4e3b\u9898**: " + parsed["subject"])
    if parsed["sender"]:
        lines.append("**\u53d1\u4ef6\u4eba**: " + parsed["sender"])
    if parsed["time"]:
        lines.append("**\u65f6\u95f4**: " + parsed["time"])
    if parsed["attachments"]:
        lines.append("**\u9644\u4ef6**:")
        for a in parsed["attachments"]:
            lines.append("- " + a + "(\U0001f4ce \u672c\u5730\u6587\u4ef6\uff0c\u65e0\u5728\u7ebf\u94fe\u63a5)")
    lines.append("")
    lines.append("---")
    lines.append("### \u539f\u6587\u5185\u5bb9")
    lines.append("")
    if parsed["body"]:
        lines.append(parsed["body"][:2000])
    else:
        lines.append("(\u65e0\u6cd5\u89e3\u6790\u90ae\u4ef6\u6b63\u6587)")
    lines.append("")
    lines.append("---")
    lines.append("*\U0001f4a1 \u4f60\u53ef\u4ee5\u76f4\u63a5\u56de\u590d\u8fd9\u6761\u6d88\u606f\uff0c\u6211\u4f1a\u6839\u636e\u90ae\u4ef6\u5185\u5bb9\u5e2e\u4f60\u5904\u7406\u3002*")
    return "\n".join(lines)

def create_fork_session(conn, original):
    now = time.time()
    fork_id = "fork_" + uuid.uuid4().hex[:14]
    sess_cols = get_columns(conn, "sessions")
    col_str = ", ".join('"{}"'.format(c) for c in sess_cols)
    placeholders = ", ".join("?" for _ in sess_cols)
    cli_data = {
        "id": fork_id, "profile": original.get("profile", "default"),
        "source": "cli", "agent": original.get("agent", "hermes"),
        "agent_mode": "", "agent_session_id": "cli",
        "agent_native_session_id": "",
        "model": original.get("model", ""), "provider": original.get("provider", ""),
        "api_mode": "",
        "title": "[\u90ae\u4ef6] {}".format(str(original.get("title", ""))[:90]),
        "started_at": now, "last_active": now, "message_count": 0,
        "tool_call_count": 0, "input_tokens": 0, "output_tokens": 0,
        "cache_read_tokens": 0, "cache_write_tokens": 0, "reasoning_tokens": 0,
        "estimated_cost_usd": 0, "cost_status": "", "preview": "",
        "is_archived": 0, "workspace": None,
    }
    values = [cli_data.get(c, None) for c in sess_cols]
    conn.execute("INSERT INTO sessions ({}) VALUES ({})".format(col_str, placeholders), values)
    messages = get_messages(conn, original["id"])
    msg_cols = [c for c in get_columns(conn, "messages") if c != "id"]
    col_str2 = ", ".join('"{}"'.format(c) for c in msg_cols)
    ph2 = ", ".join("?" for _ in msg_cols)
    for msg in messages:
        vals = [fork_id if c == "session_id" else msg.get(c, None) for c in msg_cols]
        conn.execute("INSERT INTO messages ({}) VALUES ({})".format(col_str2, ph2), vals)
    if messages:
        last_msg = messages[-1]
        if last_msg.get("role") == "user":
            parsed = parse_email(last_msg.get("content", ""))
            summary_text = build_summary(parsed)
            conn.execute(
                "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?,?,?,?)",
                (fork_id, "assistant", summary_text, now + 0.001)
            )
    conn.execute(
        "UPDATE sessions SET message_count = (SELECT COUNT(*) FROM messages WHERE session_id=?) WHERE id=?",
        (fork_id, fork_id)
    )
    conn.commit()
    log.info("FORKED {} -> {} (source: {})".format(original["id"], fork_id, original["source"]))
    return fork_id

def main():
    log.info("=" * 60)
    log.info("Email Session Fork Monitor STARTED")
    log.info("DB: {}".format(DB_PATH))
    log.info("Sources: {}".format(", ".join(FORK_SOURCES)))
    log.info("Poll interval: {}s".format(POLL_INTERVAL))
    log.info("=" * 60)
    forked_ids = load_state()
    log.info("Already tracked: {} forked sessions".format(len(forked_ids)))
    while True:
        try:
            conn = sqlite3.connect(str(DB_PATH), timeout=5)
            conn.execute("PRAGMA journal_mode=WAL")
            new_sessions = find_new_platform_sessions(conn, forked_ids)
            if new_sessions:
                log.info("Found {} new email session(s)".format(len(new_sessions)))
                for sess in new_sessions:
                    try:
                        fork_id = create_fork_session(conn, sess)
                        forked_ids.add(sess["id"])
                        save_state(forked_ids)
                        log.info("  -> Forked as: {}".format(fork_id))
                    except Exception as e:
                        log.error("Failed to fork {}: {}".format(sess["id"], e))
                        import traceback
                        log.error(traceback.format_exc())
            conn.close()
        except Exception as e:
            log.error("Monitor error: {}".format(e))
            import traceback
            log.error(traceback.format_exc())
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    if "--premark" in sys.argv:
        conn = sqlite3.connect(str(DB_PATH), timeout=5)
        conn.execute("PRAGMA journal_mode=WAL")
        forked_ids = load_state()
        conditions = " OR ".join("source='{}'".format(s) for s in FORK_SOURCES)
        rows = conn.execute("SELECT id FROM sessions WHERE ({})".format(conditions)).fetchall()
        old_count = len(forked_ids)
        for (sid,) in rows:
            forked_ids.add(sid)
        save_state(forked_ids)
        new_count = len(forked_ids)
        print("Pre-marked {} email sessions (added {})".format(new_count, new_count - old_count))
        conn.close()
    elif "--once" in sys.argv:
        conn = sqlite3.connect(str(DB_PATH), timeout=5)
        conn.execute("PRAGMA journal_mode=WAL")
        forked_ids = load_state()
        new_sessions = find_new_platform_sessions(conn, forked_ids)
        if new_sessions:
            print("Found {} new session(s)".format(len(new_sessions)))
            for sess in new_sessions:
                fork_id = create_fork_session(conn, sess)
                forked_ids.add(sess["id"])
                save_state(forked_ids)
                print("  Forked: {} -> {} (source: {})".format(sess["id"], fork_id, sess["source"]))
        else:
            print("No new sessions to fork")
        conn.close()
    else:
        main()
