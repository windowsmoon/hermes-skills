#!/usr/bin/env python3
"""
verification_gate.py — 验证门禁生成器
为 Kanban 完成的任务创建验证子任务，实现 Maker/Checker 分离。
"""

import os
import json
import sys
from datetime import datetime

HOME = os.path.expanduser("~")
KANBAN_DB = os.path.join(HOME, ".hermes", "kanban.db")
STATE_FILE = os.path.join(HOME, ".kanban-enhancer-state.json")

# 需要验证的任务类型
VERIFY_REQUIRED_KEYWORDS = [
    "代码", "部署", "发布", "release", "deploy", "上线",
    "数据", "report", "报告", "爬取", "采集",
    "配置", "config", "设置", "权限",
    "测试", "test", "qa",
]


def needs_verification(title, body):
    """判断任务是否需要验证环节"""
    text = f"{title or ''} {body or ''}".lower()
    for kw in VERIFY_REQUIRED_KEYWORDS:
        if kw.lower() in text:
            return True
    return False


def generate_verifier_task(task_id, title, assignee):
    """生成验证子任务"""
    return {
        "title": f"[Verify] {title}",
        "body": f"验证任务 #{task_id} 的执行结果是否符合预期。\n\n"
                f"## 验证要点\n"
                f"1. 结果是否完整？\n"
                f"2. 数据是否准确？\n"
                f"3. 是否有异常或错误？\n"
                f"4. 是否满足 Acceptance Criteria？\n\n"
                f"## 验证方式\n"
                f"- 检查 result 字段的 JSON 格式\n"
                f"- 检查 artifacts 中的产出物\n"
                f"- 如有错误需记录到 errors 数组中\n\n"
                f"## 验证结论\n"
                f"- [ ] ✅ 通过\n"
                f"- [ ] ❌ 不通过（需标记为 blocked，升级到 default）",
        "assignee": "default",  # 验证任务默认分配给 default（我）
        "parent_task_id": task_id,
        "priority": "high"
    }


def main():
    if not os.path.isfile(KANBAN_DB):
        print("Kanban DB 不存在")
        return
    
    import sqlite3
    conn = sqlite3.connect(KANBAN_DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # 加载状态防重复
    state = {}
    if os.path.isfile(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
        except:
            state = {}
    
    verified_count = 0
    
    try:
        # 找新完成的任务（completed_at 在最近1小时内）
        one_hour_ago = datetime.now().isoformat()
        cur.execute("""
            SELECT id, title, body, assignee, result 
            FROM tasks 
            WHERE status='done' 
              AND completed_at > datetime('now', '-1 hour')
            ORDER BY completed_at DESC
        """)
        
        for row in cur.fetchall():
            task_id = row['id']
            verify_key = f"verified_{task_id}"
            
            if state.get(verify_key):
                continue  # 已处理过
            
            if not needs_verification(row['title'], row['body'] or ''):
                state[verify_key] = False
                continue  # 不需要验证
            
            # 生成验证任务
            verifier = generate_verifier_task(task_id, row['title'], row['assignee'])
            print(f"🔒 需要验证: #{task_id} {row['title']}")
            print(f"   验证任务: {verifier['title']}")
            print(f"   分配给: {verifier['assignee']}")
            verified_count += 1
            state[verify_key] = True
    
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            print("Kanban 表还不存在，跳过")
        else:
            raise
    
    # 保存状态
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    
    conn.close()
    
    if verified_count == 0:
        print("✅ 无需验证的新任务")


if __name__ == "__main__":
    main()