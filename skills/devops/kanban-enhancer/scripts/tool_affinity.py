#!/usr/bin/env python3
"""
tool_affinity.py — 工具亲和性检查器（独立脚本）
用于 Kanban decompose 前/后验证任务分配是否合理。
读取 Profile能力矩阵.md 中的工具映射表，与任务文本关键词匹配。
"""

import os
import json
import re

# 直接从 Profile能力矩阵.md 同步的工具映射表
TOOL_MAP = {
    # 任务关键词 → (所需工具, 允许的Profile列表)
    "apify|scrape|crawl|extract|采集|爬取|抓取|电商|淘宝|京东|抖音|商品|数据采集": {
        "tool": "Apify MCP / Tabbit MCP",
        "profiles": ["bigdata-director", "default"]
    },
    "trendradar|热点|热搜|趋势|hot|trend|新闻|话题": {
        "tool": "TrendRadar MCP",
        "profiles": ["operations-director", "default"]
    },
    "feishu|飞书|文档|表格|推送|base|bitable": {
        "tool": "Feishu CLI / Docx API",
        "profiles": ["operations-director", "default"]
    },
    "opencode|code|开发|重构|写代码|代码审查|架构|工程|build|dev|feature": {
        "tool": "OpenCode CLI / ACP",
        "profiles": ["engineering-director", "default"]
    },
    "pm.skills|prd|产品|需求|用户|竞品|market|strategy|okr|路线图|商业模式|customer": {
        "tool": "pm-skills (68项)",
        "profiles": ["product-manager", "default"]
    },
    "test|qa|测试|质量|验证|用例|bug|缺陷|回归": {
        "tool": "test-scenarios",
        "profiles": ["qa-director", "default"]
    },
    "disk|cleanup|清理|维护|backup|sre|运维|诊断|备份": {
        "tool": "系统 CLI",
        "profiles": ["helper", "default"]
    },
    "design|ui|ux|设计|配色|布局|图标|视觉|banner|品牌": {
        "tool": "vision_analyze + image_generate",
        "profiles": ["designer", "default"]
    },
    "tabbit|浏览器|antidetect|反爬|页面": {
        "tool": "Tabbit Browser MCP",
        "profiles": ["bigdata-director", "default"]
    },
}


def check_task(title, body, assignee):
    """检查单个任务的工具亲和性"""
    text = f"{title or ''} {body or ''}".lower()
    issues = []
    
    for pattern, info in TOOL_MAP.items():
        matched = False
        for keyword in pattern.split("|"):
            if keyword.lower() in text:
                matched = True
                break
        if matched and assignee not in info["profiles"]:
            issues.append({
                "tool": info["tool"],
                "required_profiles": info["profiles"],
                "current_assignee": assignee,
                "suggestion": f"建议分配给 {', '.join(info['profiles'])}"
            })
    
    return issues


def suggest_assignee(title, body):
    """根据任务内容推荐分配的 Profile"""
    text = f"{title or ''} {body or ''}".lower()
    
    scores = {}
    for pattern, info in TOOL_MAP.items():
        for keyword in pattern.split("|"):
            if keyword.lower() in text:
                for profile in info["profiles"]:
                    scores[profile] = scores.get(profile, 0) + 1
                break
    
    if not scores:
        return None
    
    # 按得分排序，排除 default（default 是兜底，不是首选）
    sorted_profiles = sorted(scores.items(), key=lambda x: -x[1])
    # 如果 default 得分最高但其他 profile 也有分，选其他 profile
    for profile, score in sorted_profiles:
        if profile != "default":
            return profile
    
    return sorted_profiles[0][0] if sorted_profiles else "default"


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 4:
        title = sys.argv[1]
        body = sys.argv[2]
        assignee = sys.argv[3]
        issues = check_task(title, body, assignee)
        if issues:
            print(json.dumps(issues, ensure_ascii=False, indent=2))
        else:
            print("✅ 工具亲和性检查通过")
    else:
        print(f"用法: python {sys.argv[0]} <title> <body> <assignee>")