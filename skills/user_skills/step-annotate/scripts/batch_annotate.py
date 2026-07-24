#!/usr/bin/env python3
"""
batch_annotate.py — 批量截图编号批注工具

用法：
  python batch_annotate.py <annotations.json>

annotations.json 由 Hermes Agent 根据口播稿 + vision 分析自动生成。
输出：与截图同目录创建"标注完成/" 子文件夹。
"""

import json
import os
import sys
from PIL import Image, ImageDraw, ImageFont




def detect_red_boxes(img):
    """检测用户手绘的红色方框（约定：用户用红色框出需要标注的区域）
    
    返回 [(x, y, w, h), ...] 列表，按左上到右下排序。
    检测策略：扫描红色像素（R>200, G<100, B<100）形成的矩形轮廓。
    """
    import numpy as np
    arr = np.array(img.convert("RGB"))
    
    # 红色掩码：R >> G,B 且有一定饱和度
    r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
    red_mask = (r > 180) & (g < 100) & (b < 100) & (r - g > 80)
    
    # 找出红色像素的行列范围
    rows = np.any(red_mask, axis=1)
    cols = np.any(red_mask, axis=0)
    
    if not rows.any() or not cols.any():
        return []  # 没找到红色框
    
    # 找连通区域（简单实现：行扫描分段）
    y_indices = np.where(rows)[0]
    x_indices = np.where(cols)[0]
    
    # 分组：找出行/列中的连续段
    def find_segments(indices, gap=10):
        segments = []
        start = indices[0]
        prev = indices[0]
        for i in indices[1:]:
            if i - prev > gap:
                segments.append((int(start), int(prev)))
                start = i
            prev = i
        segments.append((int(start), int(prev)))
        return segments
    
    y_segments = find_segments(y_indices)
    x_segments = find_segments(x_indices)
    
    # 每对 y段和 x段 构成一个框
    boxes = []
    for ys, ye in y_segments:
        for xs, xe in x_segments:
            # 检查这片区域确实有红色像素
            sub = red_mask[ys:ye+1, xs:xe+1]
            red_ratio = sub.sum() / sub.size if sub.size > 0 else 0
            if red_ratio > 0.05:  # 至少 5% 红色像素
                # 收缩到实际红色边界
                red_rows = np.any(sub, axis=1)
                red_cols = np.any(sub, axis=0)
                if red_rows.any() and red_cols.any():
                    ry = np.where(red_rows)[0]
                    rx = np.where(red_cols)[0]
                    boxes.append((
                        int(xs + rx[0]), int(ys + ry[0]),
                        int(rx[-1] - rx[0] + 1), int(ry[-1] - ry[0] + 1)
                    ))
    
    # 去重：合并重叠的框
    merged = []
    for box in boxes:
        overlap = False
        for i, mb in enumerate(merged):
            # 检查是否重叠
            if (box[0] < mb[0] + mb[2] and box[0] + box[2] > mb[0] and
                box[1] < mb[1] + mb[3] and box[1] + box[3] > mb[1]):
                # 合并
                merged[i] = (
                    min(box[0], mb[0]), min(box[1], mb[1]),
                    max(box[0] + box[2], mb[0] + mb[2]) - min(box[0], mb[0]),
                    max(box[1] + box[3], mb[1] + mb[3]) - min(box[1], mb[1])
                )
                overlap = True
                break
        if not overlap:
            merged.append(box)
    
    # 按左上到右下排序
    merged.sort(key=lambda b: (b[1], b[0]))
    return merged



def load_font(size):
    candidates = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/yahei.ttf",
        "/System/Library/Fonts/PingFang.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def draw_annotation(draw, img_w, img_h, anno, font):
    x, y, w, h = anno["x"], anno["y"], anno["width"], anno["height"]
    number = anno["number"]
    text = anno["text"]

    style = anno.get("style", {})
    box_color = tuple(style.get("box_color", [255, 69, 0]))
    box_width = style.get("box_width", 3)
    arrow_color = tuple(style.get("arrow_color", [255, 69, 0]))
    font_size = style.get("font_size", 16)
    bg_color = tuple(style.get("number_bg_color", [255, 69, 0]))
    fg_color = tuple(style.get("number_fg_color", [255, 255, 255]))
    label_ox = style.get("label_offset_x", 8)
    label_oy = style.get("label_offset_y", -8)
    keep_box = anno.get("keep_existing_box", False)

    # 如果用户已经画了红框，不再重复画框
    if not keep_box:
        draw.rectangle([x, y, x + w, y + h], outline=box_color, width=box_width)
    num_r = font_size + 4
    cx = x + label_ox
    cy = y + label_oy
    draw.ellipse([cx - num_r, cy - num_r, cx + num_r, cy + num_r],
                 fill=bg_color, outline=bg_color)
    num_text = str(number)
    bbox = font.getbbox(num_text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((cx - tw // 2, cy - th // 2 - 1), num_text, fill=fg_color, font=font)
    label_x = cx + num_r + 6
    label_y = cy - font_size // 2
    draw.text((label_x, label_y), text, fill=box_color, font=font)
    center_x = x + w // 2
    center_y = y + h // 2
    arrow_start = (label_x, label_y + font_size // 2)
    arrow_end = (center_x, center_y)
    draw.line([arrow_start, arrow_end], fill=arrow_color, width=2)
    dx = arrow_end[0] - arrow_start[0]
    dy = arrow_end[1] - arrow_start[1]
    length = (dx * dx + dy * dy) ** 0.5
    if length > 0:
        dx /= length
        dy /= length
        al = 10
        left = (arrow_end[0] - dx * al + dy * al * 0.4,
                arrow_end[1] - dy * al - dx * al * 0.4)
        right = (arrow_end[0] - dx * al - dy * al * 0.4,
                 arrow_end[1] - dy * al + dx * al * 0.4)
        draw.line([arrow_end, left], fill=arrow_color, width=2)
        draw.line([arrow_end, right], fill=arrow_color, width=2)


def process_batch(annotations):
    images = annotations["images"]
    global_style = annotations.get("style", {})
    detect_boxes = annotations.get("detect_boxes", False)
    font = load_font(global_style.get("font_size", 16))
    input_dir = None
    for img_path in images:
        d = os.path.dirname(os.path.abspath(img_path))
        if input_dir is None:
            input_dir = d
        break
    if input_dir:
        # 输出目录名可自定义
        output_dir_name = annotations.get("output_dir", "标注完成")
        output_base = os.path.join(input_dir, output_dir_name)
    else:
        output_base = "标注完成"
    os.makedirs(output_base, exist_ok=True)
    results = []
    step = 0
    for img_path, annos in images.items():
        if not os.path.exists(img_path):
            print(f"跳过（文件不存在）：{img_path}")
            continue
        img = Image.open(img_path).convert("RGBA")
        draw = ImageDraw.Draw(img)
        
        # 如果启用了红框检测，先检测用户画的红框
        if detect_boxes:
            red_boxes = detect_red_boxes(img)
            if red_boxes and not annos:
                # 自动为每个红框生成标注（按显示顺序）
                for bx, by, bw, bh in red_boxes:
                    step += 1
                    # 从映射表中找对应的文字
                    texts_map = annotations.get("box_texts", {})
                    box_key = f"{step}"
                    text = texts_map.get(box_key, f"步骤{step}")
                    anno = {
                        "number": step,
                        "text": text,
                        "x": bx, "y": by, "width": bw, "height": bh,
                        "keep_existing_box": True  # 保留用户的红框
                    }
                    merged_style = {**global_style, **anno.get("style", {})}
                    anno_with_style = {**anno, "style": merged_style}
                    draw_annotation(draw, img.width, img.height, anno_with_style, font)
                # 生成输出文件名
                first_text = list(annotations.get("box_texts", {}).values())[0] if annotations.get("box_texts") else "标注"
                out_name = f"步骤1-{first_text}" if first_text else os.path.basename(img_path)
            else:
                # 有显式标注时走正常流程
                for anno in annos:
                    step += 1
                    merged_style = {**global_style, **anno.get("style", {})}
                    anno_with_style = {**anno, "style": merged_style}
                    draw_annotation(draw, img.width, img.height, anno_with_style, font)
                first_anno = annos[0] if annos else {}
                out_name = first_anno.get("output_name", "")
                if not out_name:
                    prefix = f"步骤{len(results)+1}-"
                    first_text = first_anno.get("text", "图")
                    out_name = f"{prefix}{first_text}"
        else:
            # 常规流程：使用显式标注
            for anno in annos:
                step += 1
                merged_style = {**global_style, **anno.get("style", {})}
                anno_with_style = {**anno, "style": merged_style}
                draw_annotation(draw, img.width, img.height, anno_with_style, font)
            first_anno = annos[0] if annos else {}
            out_name = first_anno.get("output_name", "")
            if not out_name:
                prefix = f"步骤{len(results)+1}-"
                first_text = first_anno.get("text", "图")
                out_name = f"{prefix}{first_text}"
        
        ext = os.path.splitext(os.path.basename(img_path))[1] or ".png"
        if not out_name.endswith(ext):
            out_name += ext
        out_path = os.path.join(output_base, out_name)
        img.convert("RGB").save(out_path, quality=95)
        results.append((img_path, out_path))
        print(f"  {os.path.basename(img_path)} -> {out_name}")
    return results


def main():
    if len(sys.argv) < 2:
        print("用法: python batch_annotate.py <annotations.json>")
        sys.exit(1)
    config_path = sys.argv[1]
    with open(config_path, "r", encoding="utf-8") as f:
        annotations = json.load(f)
    results = process_batch(annotations)
    if results:
        out_dir = os.path.dirname(results[0][1])
        print(f"全部完成！输出目录：{out_dir}")
    else:
        print("没有文件被处理")


if __name__ == "__main__":
    main()
