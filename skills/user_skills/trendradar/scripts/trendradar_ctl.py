#!/usr/bin/env python3
"""trendradar_ctl.py — 动态控制 TrendRadar 抓取逻辑"""
import subprocess, os, sys

TREND_DIR = os.path.expanduser("~/Developer/TrendRadar")
PYTHON = os.path.join(TREND_DIR, ".venv", "Scripts", "python.exe")
FW_PATH = os.path.join(TREND_DIR, "config", "frequency_words.txt")

def set_keywords(keywords):
    """设置关键词（带 AI 语义理解）"""
    content = f"# 由 Hermes Agent 动态设置\n[GLOBAL_FILTER]\n\n[WORD_GROUPS]\n{keywords}\n"
    with open(FW_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    return f"关键词已设为: {keywords}"

def clear_keywords():
    """清空关键词 = 全量返回"""
    content = "# 空 = 全量返回，不过滤\n[GLOBAL_FILTER]\n\n[WORD_GROUPS]\n"
    with open(FW_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    return "关键词已清空，将返回全部热点"

def run():
    """运行 TrendRadar"""
    result = subprocess.run(
        [PYTHON, "-m", "trendradar"],
        capture_output=True, text=True, cwd=TREND_DIR, timeout=300
    )
    return result.stdout, result.stderr

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python trendradar_ctl.py [set|clear|run] [关键词]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "set" and len(sys.argv) > 2:
        print(set_keywords(sys.argv[2]))
    elif cmd == "clear":
        print(clear_keywords())
    elif cmd == "run":
        out, err = run()
        print(out[-500:] if out else "")
        if err:
            print(f"stderr: {err[-200:]}")
    else:
        print(f"未知命令: {cmd}")
