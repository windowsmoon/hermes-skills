#!/usr/bin/env python3
"""
buyin-harvester / scripts/state.py
采集状态管理

功能:
  - 维护采集进度状态（持久化到 state.json）
  - 记录已采集的数量
  - 去重key管理
  - "到底"检测逻辑
  - 进度查询

用法:
  from state import CollectionState
  state = CollectionState("state.json")
  state.init()
  state.add_records(new_records)
  state.should_stop()  → True/False
  state.summary()      → 统计信息
"""

import json
import hashlib
import time
from pathlib import Path


class CollectionState:
    """采集状态管理器"""
    
    def __init__(self, state_path: str = None):
        if state_path is None:
            state_path = Path(__file__).parent / "collect_state.json"
        self.path = Path(state_path)
        self.data = self._load()
    
    def _load(self) -> dict:
        if self.path.exists():
            try:
                with open(self.path, encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return {}
    
    def _save(self):
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def init(self, target: int = 50):
        """初始化新采集"""
        self.data = {
            "records": [],
            "seen_keys": {},        # md5 → true, 去重用
            "scroll_count": 0,
            "empty_rounds": 0,      # 连续无新增轮次
            "total_fetched": 0,
            "target": target,
            "status": "collecting",  # collecting | done | pause | error
            "start_time": time.time(),
            "last_round_time": time.time(),
            "errors": [],
        }
        self._save()
    
    def _make_key(self, record: dict) -> str:
        """生成去重key: md5(博主+时间+摘要[:30])"""
        raw = f"{record.get('博主名称','')}|{record.get('发布时间','')}|{record.get('视频摘要','')[:30]}"
        return hashlib.md5(raw.encode()).hexdigest()
    
    def add_records(self, new_records: list[dict]) -> int:
        """
        添加新记录（自动去重）
        返回本次新增数量
        """
        if "records" not in self.data:
            self.init()
        
        added = 0
        for r in new_records:
            key = self._make_key(r)
            if key not in self.data["seen_keys"]:
                self.data["seen_keys"][key] = True
                self.data["records"].append(r)
                added += 1
        
        if added == 0:
            self.data["empty_rounds"] += 1
        else:
            self.data["empty_rounds"] = 0
        
        self.data["total_fetched"] = len(self.data["records"])
        self.data["last_round_time"] = time.time()
        self._save()
        return added
    
    def increment_scroll(self):
        """增加滚动计数"""
        self.data["scroll_count"] += 1
        self._save()
    
    def should_stop(self) -> tuple[bool, str]:
        """
        判断是否应该停止采集
        返回 (True/False, 原因)
        """
        if self.data.get("status") != "collecting":
            return True, self.data.get("status", "unknown")
        
        # 达到目标量
        if self.data["total_fetched"] >= self.data["target"]:
            self.data["status"] = "done"
            self._save()
            return True, f"已达到目标量 {self.data['target']} 条"
        
        # 连续空转
        if self.data["empty_rounds"] >= 3:
            self.data["status"] = "done"
            self._save()
            return True, "连续3次无新增数据，判定已到底"
        
        return False, "继续采集"
    
    def pause(self, reason: str = ""):
        """暂停采集"""
        self.data["status"] = "pause"
        self.data["pause_reason"] = reason
        self._save()
    
    def resume(self):
        """恢复采集"""
        self.data["status"] = "collecting"
        if "pause_reason" in self.data:
            del self.data["pause_reason"]
        self._save()
    
    def error(self, msg: str):
        """记录错误"""
        self.data.setdefault("errors", []).append({
            "time": time.time(),
            "msg": msg
        })
        self._save()
    
    def summary(self) -> dict:
        """生成采集统计"""
        elapsed = time.time() - self.data.get("start_time", time.time())
        return {
            "total": self.data.get("total_fetched", 0),
            "target": self.data.get("target", 50),
            "scrolls": self.data.get("scroll_count", 0),
            "empty_rounds": self.data.get("empty_rounds", 0),
            "status": self.data.get("status", "unknown"),
            "elapsed_seconds": round(elapsed, 1),
            "errors": len(self.data.get("errors", [])),
        }
    
    def reset(self):
        """完全重置状态"""
        self.data = {}
        self.path.unlink(missing_ok=True)
    
    def get_records(self) -> list[dict]:
        """获取已采集的记录"""
        return self.data.get("records", [])


# ── CLI ───────────────────────────────────────────────
if __name__ == '__main__':
    import sys
    
    state = CollectionState()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "init":
            target = int(sys.argv[2]) if len(sys.argv) > 2 else 50
            state.init(target)
            print(f"✅ 初始化完成，目标 {target} 条")
        elif cmd == "summary":
            s = state.summary()
            print(f"📊 采集进度: {s['total']}/{s['target']} 条")
            print(f"  滚动 {s['scrolls']} 次 | 空转 {s['empty_rounds']} 轮")
            print(f"  状态: {s['status']} | 耗时 {s['elapsed_seconds']}s")
            print(f"  错误: {s['errors']} 个")
        elif cmd == "reset":
            state.reset()
            print("🧹 已重置")
        elif cmd == "pause":
            reason = sys.argv[2] if len(sys.argv) > 2 else "手动暂停"
            state.pause(reason)
            print(f"⏸ 已暂停: {reason}")
        elif cmd == "resume":
            state.resume()
            print("▶️ 已恢复")
        elif cmd == "records":
            recs = state.get_records()
            print(json.dumps(recs, ensure_ascii=False, indent=2))
            print(f"\n--- 共 {len(recs)} 条 ---")
        else:
            print(f"未知命令: {cmd}")
    else:
        state.summary()
