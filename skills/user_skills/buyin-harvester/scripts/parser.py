#!/usr/bin/env python3
"""
buyin-harvester / scripts/parser.py
巨量百应爆款视频页面文本 → 结构化记录

用法:
  from parser import parse_hot_video_text
  records = parse_hot_video_text(raw_text)

输入: tabbit_extract(type="text") 或 tabbit_readability() 返回的原始文本
输出: list[dict]  每条视频的结构化数据

版块分割标记: "总播放量" 是每个视频数据块的分隔点。
每个视频块结构:
  [标题标签行]        → 视频标题和话题标签
  [博主名称行]         → 发布者
  [发布时间行]         → yyyy/MM/dd HH:mm:ss
  [时长行]             → N分N秒 / N秒
  [商品摘要行]         → 商品名称/描述
  "总播放量" 标记
  [数字]               → 播放量数字
  [万+]                → 单位
  [数字]               → 新增播放量数字
  [万+]                → 单位
  "已选类目结算金额"
  [金额]               → 如 "10万-50万"
  "总点赞量"
  [数字]               → 点赞数
  [+]                  → 单位标记
"""

import re
import json
import sys


def parse_hot_video_text(raw_text: str) -> list[dict]:
    """
    解析巨量百应爆款视频页的原始文本，返回结构化记录列表。
    
    Args:
        raw_text: 从 tabbit_extract() 或 tabbit_readability() 获取的页面文本
        
    Returns:
        记录列表，每项包含：
          title_tags, author_name, publish_time, duration,
          product_summary, total_views, added_views,
          settlement_amount, total_likes
    """
    if not raw_text or not raw_text.strip():
        return []

    # 按"总播放量"分割
    splits = raw_text.split('总播放量')
    if len(splits) < 2:
        # 可能没有"总播放量"标记，尝试整块解析
        return []

    def make_record(meta_lines, data_lines):
        """从元数据+数据行构建一条记录"""
        meta_lines = [l.strip() for l in meta_lines if l.strip()]
        data_lines = [l.strip() for l in data_lines if l.strip()]
        
        if len(meta_lines) < 5 or len(data_lines) < 9:
            return None
        
        record = {
            '视频标题与标签': meta_lines[0] if len(meta_lines) > 0 else '',
            '博主名称':        meta_lines[1] if len(meta_lines) > 1 else '',
            '发布时间':        meta_lines[2] if len(meta_lines) > 2 else '',
            '视频时长':        meta_lines[3] if len(meta_lines) > 3 else '',
            '视频摘要':        meta_lines[4] if len(meta_lines) > 4 else '',
        }
        
        # 解析data_lines:
        # data[0]=播放数字, [1]=万+, [2]=新增数字, [3]=万+, 
        # [4]="已选类目结算金额", [5]=金额, [6]="总点赞量", [7]=点赞数字, [8]=+
        idx = 0
        if len(data_lines) >= 9:
            record['总播放量']        = data_lines[0] + data_lines[1]
            record['新增播放量']      = data_lines[2] + data_lines[3]
            record['已选类目结算金额'] = data_lines[5]
            record['总点赞量']        = data_lines[7] + data_lines[8]
        else:
            record['总播放量']        = ''
            record['新增播放量']      = ''
            record['已选类目结算金额'] = ''
            record['总点赞量']        = ''
        
        return record

    records = []
    
    # 第一条视频: meta=splits[0], data=splits[1][:9]
    first_meta = splits[0].strip().split('\n')
    first_data = splits[1].strip().split('\n')[:9]
    r = make_record(first_meta, first_data)
    if r:
        records.append(r)
    
    # 第2-5条视频（视页面加载情况而定）
    for i in range(1, len(splits)):
        sec = splits[i].strip().split('\n')
        meta_part = sec[-5:] if len(sec) > 9 else None
        data_part = sec[:9] if len(sec) >= 9 else sec
        
        if meta_part and len(data_part) >= 9:
            r = make_record(meta_part, data_part)
            if r:
                records.append(r)
    
    return records


def dedup_records(records: list[dict], seen_keys: set = None) -> tuple[list[dict], set]:
    """
    去重：基于 博主名称 + 发布时间 + 视频摘要[:30] 的MD5哈希
    
    Args:
        records: 待去重的记录列表
        seen_keys: 已有的key集合（可传入空set）
        
    Returns:
        (new_records, updated_seen_keys)
    """
    import hashlib
    
    if seen_keys is None:
        seen_keys = set()
    
    new_records = []
    for r in records:
        raw_key = f"{r.get('博主名称','')}|{r.get('发布时间','')}|{r.get('视频摘要','')[:30]}"
        key = hashlib.md5(raw_key.encode()).hexdigest()
        if key not in seen_keys:
            seen_keys.add(key)
            new_records.append(r)
    
    return new_records, seen_keys


def records_to_json(records: list[dict], indent=2) -> str:
    """将记录格式化为JSON"""
    return json.dumps(records, ensure_ascii=False, indent=indent)


# ── CLI ───────────────────────────────────────────────
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding='utf-8') as f:
            text = f.read()
    else:
        text = sys.stdin.read()
    
    records = parse_hot_video_text(text)
    new_recs, _ = dedup_records(records)
    
    print(json.dumps(new_recs, ensure_ascii=False, indent=2))
    print(f"\n--- 共 {len(new_recs)} 条记录 ---", file=sys.stderr)
