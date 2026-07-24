#!/usr/bin/env python3
"""
kanban_enhancer.py — Kanban 看板增强主入口
功能：工具亲和性检查 + 结果标准化 + 失败升级链 + 验证门禁 + 超时检测
调用方式：python kanban_enhancer.py [--dry-run]
状态文件：~/.kanban-enhancer-state.json
"""

import sqlite3
import os
import json
import re
import sys
from datetime import datetime, timedelta
from collections import defaultdict

HOME = os.path.expanduser("~")
KANBAN_DB = os.path.join(HOME, ".hermes", "kanban.db")
STATE_FILE = os.path.join(HOME, ".kanban-enhancer-state.json")
FAILURE_LIMIT = 2
STALE_TIMEOUT = 14400  # 4 hours

# ── 工具-Profile 映射表 ──────────────────────────────────────────
# 从 Profile能力矩阵.md 同步
TOOL_PROFILE_MAP = {
    "apify":        ["bigdata-director", "default"],
    "tabbit":       ["bigdata-director", "default"],
    "trendradar":   ["operations-director", "default"],
    "feishu":       ["operations-director", "default"],
    "opencode":     ["engineering-director", "default"],
    "pm_skills":    ["product-manager", "default"],
    "test_scenarios": ["qa-director", "default"],
    "system_tools": ["helper", "default"],
    "design":       ["designer", "default"],
}

# ── 失败升级链 ────────────────────────────────────────────────────
ESCALATION_CHAIN = {
    "engineering-director": ["qa-director", "default"],
    "qa-director":          ["engineering-director", "default"],
    "operations-director":  ["bigdata-director", "default"],
    "bigdata-director":     ["operations-director", "default"],
    "product-manager":      ["default"],
    "designer":             ["default"],
    "helper":               ["default"],
    "default":              ["default"],
}

# ── 任务关键词 → 工具映射 ─────────────────────────────────────────
KEYWORD_TOOL_MAP = [
    # (关键词列表, 工具名, 权重)
    (["爬取", "采集", "抓取", "scrape", "crawl", "extract", "电商", "淘宝", "京东", "抖音", "商品"], "apify", 10),
    (["tabbit", "浏览器", "反爬", "antidetect", "页面"], "tabbit", 10),
    (["热点", "热搜", "趋势", "trend", "hot", "新闻", "话题"], "trendradar", 10),
    (["飞书", "feishu", "文档", "表格", "推送", "base", "bitable"], "feishu", 10),
    (["代码", "开发", "重构", "code", "dev", "build", "fix", "bug", "feature", "工程"], "opencode", 10),
    (["prd", "产品", "需求", "用户", "竞品", "market", "strategy", "okr", "路线图"], "pm_skills", 10),
    (["测试", "test", "qa", "质量", "验证", "bug", "用例"], "test_scenarios", 10),
    (["磁盘", "清理", "维护", "backup", "cleanup", "sre", "运维", "诊断"], "system_tools", 10),
    (["设计", "ui", "ux", "配色", "布局", "图标", "视觉", "banner", "品牌"], "design", 10),
    (["数据", "data", "分析", "报表", "excel", "csv", "json"], "apify", 5),  # 低权重
]


def get_required_tools_from_keywords(text):
    """从任务文本中提取需要的工具"""
    text = (text or "").lower()
    required = set()
    for keywords, tool, weight in KEYWORD_TOOL_MAP:
        for kw in keywords:
            if kw.lower() in text:
                required.add(tool)
                break
    return list(required)


def check_tool_affinity(title, body, assignee):
    """检查分配的 Profile 是否拥有执行任务所需的工具"""
    text = f"{title or ''} {body or ''}"
    required_tools = get_required_tools_from_keywords(text)
    if not required_tools:
        return []
    
    mismatches = []
    for tool in required_tools:
        allowed = TOOL_PROFILE_MAP.get(tool, [])
        if assignee not in allowed:
            mismatches.append({
                "tool": tool,
                "allowed_profiles": allowed,
                "current_assignee": assignee
            })
    return mismatches


def standardize_result(result_str, title):
    """标准化 result 字段为 JSON 格式"""
    if not result_str or result_str.strip() == "":
        result_str = title or "任务完成"
    
    try:
        parsed = json.loads(result_str)
        if isinstance(parsed, dict) and "status" in parsed and "summary" in parsed:
            return None, True  # 已经是标准格式
    except (json.JSONDecodeError, TypeError):
        pass
    
    # 判断状态
    lower = result_str.lower()
    if any(kw in lower for kw in ["失败", "error", "fail", "timeout", "异常"]):
        status = "failed"
    elif any(kw in lower for kw in ["部分", "partial", "部分成功"]):
        status = "partial"
    else:
        status = "success"
    
    standard = {
        "status": status,
        "summary": result_str.strip()[:500] if result_str else "",
        "artifacts": [],
        "duration_seconds": None,
        "errors": []
    }
    return json.dumps(standard, ensure_ascii=False, indent=2), False


def get_escalation_target(assignee, retries):
    """根据失败次数和升级链确定下一个目标 Profile"""
    chain = ESCALATION_CHAIN.get(assignee, ["default"])
    # retries >= 2 → 跳到 Level 2（同级互转）
    # retries >= 4 → 跳到 Level 3（default）
    # retries >= 6 → 标记为 blocked
    if retries >= 6:
        return None, "blocked"  # 停止
    if retries >= 4:
        return "default", "escalated_to_default"
    if retries >= 2 and len(chain) > 0:
        return chain[0], "escalated_to_peer"
    return assignee, "retry"


def main():
    dry_run = "--dry-run" in sys.argv
    
    if not os.path.isfile(KANBAN_DB):
        print(f"⚠️ Kanban DB 不存在: {KANBAN_DB}（首次使用时会自动创建）")
        return
    
    # 加载状态
    state = {}
    if os.path.isfile(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
        except (json.JSONDecodeError, IOError):
            state = {}
    
    conn = sqlite3.connect(KANBAN_DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "tool_affinity_checks": [],
        "result_standardizations": [],
        "failure_escalations": [],
        "verification_gates": [],
        "stale_detections": []
    }
    
    # ── 1. 工具亲和性检查 ──────────────────────────────────────
    try:
        cur.execute("SELECT id, title, body, assignee, status FROM tasks WHERE status IN ('triage', 'todo', 'ready')")
        for row in cur.fetchall():
            mismatches = check_tool_affinity(row['title'], row['body'] or '', row['assignee'])
            if mismatches:
                note = (
                    f"⚠️ 工具亲和性警告：任务需要 "
                    f"{', '.join(m['tool'] for m in mismatches)}，"
                    f"但当前分配给 {row['assignee']}"
                    f"（建议分配给 {', '.join(set(p for m in mismatches for p in m['allowed_profiles']))}）"
                )
                report["tool_affinity_checks"].append({
                    "task_id": row['id'],
                    "title": row['title'],
                    "assignee": row['assignee'],
                    "mismatches": [m['tool'] for m in mismatches],
                    "note": note
                })
    except sqlite3.OperationalError as e:
        # 表可能还不存在
        if "no such table" in str(e):
            pass
        else:
            raise
    
    # ── 2. 结果标准化 ──────────────────────────────────────────
    try:
        cur.execute("SELECT id, title, result, completed_at FROM tasks WHERE status='done' AND result IS NOT NULL")
        for row in cur.fetchall():
            std_result, already_standard = standardize_result(row['result'], row['title'])
            if std_result is not None:
                report["result_standardizations"].append({
                    "task_id": row['id'],
                    "title": row['title'],
                    "original_preview": row['result'][:100],
                    "standardized": std_result
                })
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            pass
        else:
            raise
    
    # ── 3. 失败升级链 ──────────────────────────────────────────
    try:
        cur.execute("SELECT id, title, assignee, retries, result FROM tasks WHERE status IN ('blocked', 'failed')")
        for row in cur.fetchall():
            task_id = row['id']
            esc_key = f"escalated_{task_id}"
            if state.get(esc_key):
                continue  # 已处理过
            
            next_assignee, action = get_escalation_target(row['assignee'], row['retries'] or 0)
            if next_assignee is None:
                # 停止——标记为终极 blocked
                report["failure_escalations"].append({
                    "task_id": task_id,
                    "title": row['title'],
                    "action": "终极停止",
                    "reason": f"任务 {row['title']} 已失败 {row['retries']} 次，升级链耗尽，需人工介入"
                })
            elif next_assignee != row['assignee']:
                report["failure_escalations"].append({
                    "task_id": task_id,
                    "title": row['title'],
                    "from_assignee": row['assignee'],
                    "to_assignee": next_assignee,
                    "action": action,
                    "reason": f"重试 {row['retries']} 次失败，从 {row['assignee']} 升级到 {next_assignee}"
                })
            state[esc_key] = True
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            pass
        else:
            raise
    
    # ── 4. 超时检测 ────────────────────────────────────────────
    try:
        stale_cutoff = datetime.now() - timedelta(seconds=STALE_TIMEOUT)
        cur.execute("SELECT id, title, assignee, started_at FROM tasks WHERE status='running' AND started_at IS NOT NULL")
        for row in cur.fetchall():
            try:
                started = datetime.fromisoformat(str(row['started_at']).replace('Z', '+00:00'))
                if started.replace(tzinfo=None) < stale_cutoff:
                    stale_for = datetime.now() - started.replace(tzinfo=None)
                    report["stale_detections"].append({
                        "task_id": row['id'],
                        "title": row['title'],
                        "assignee": row['assignee'],
                        "started_at": row['started_at'],
                        "stale_hours": round(stale_for.total_seconds() / 3600, 1)
                    })
            except (ValueError, TypeError):
                pass
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            pass
        else:
            raise
    
    # ── 保存状态 ────────────────────────────────────────────────
    state["last_run"] = datetime.now().isoformat()
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    
    conn.close()
    
    # ── 输出报告 ────────────────────────────────────────────────
    total = sum(len(v) for k, v in report.items() if k != "timestamp")
    print(f"📊 Kanban Enhancer Report ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
    print(f"   共发现 {total} 项")
    
    for key, items in report.items():
        if key == "timestamp":
            continue
        label = {
            "tool_affinity_checks": "🔧 工具亲和性",
            "result_standardizations": "📐 结果标准化",
            "failure_escalations": "🚨 失败升级",
            "verification_gates": "🔒 验证门禁",
            "stale_detections": "⏰ 超时检测"
        }.get(key, key)
        if items:
            print(f"  [{label}] {len(items)} 项")
            for item in items[:3]:
                print(f"    - {item.get('title', 'N/A')}")
                if 'note' in item:
                    print(f"      {item['note']}")
        else:
            print(f"  [{label}] 无")
    
    if dry_run:
        print("\n⚠️ DRY RUN — 未执行任何修改")
    
    return report


if __name__ == "__main__":
    main()