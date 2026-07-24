"""
universal_scraper reporter.py — 输出格式化：CSV / JSON / Markdown
"""
import os, json, csv
from datetime import datetime

def export_csv(records, output_path):
    if not records:
        return
    keys = records[0].keys()
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(records)

def export_json(records, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def export_markdown(records, output_path):
    lines = []
    for r in records:
        lines.append(f"## Page {r.get('page', '?')}")
        lines.append(f"URL: {r.get('url', '')}")
        lines.append(f"Content: {r.get('content_preview', '')}")
        if r.get('images'):
            for img in r['images'][:5]:
                lines.append(f"![]({img})")
        lines.append("---")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def create_export_dir(domain):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = os.path.expanduser(f"~/Desktop/scraped_{domain}_{ts}")
    os.makedirs(out, exist_ok=True)
    return out

def export_all(records, domain, summary):
    outdir = create_export_dir(domain)
    export_csv(records, os.path.join(outdir, "data.csv"))
    export_json(records, os.path.join(outdir, "data.json"))
    export_markdown(records, os.path.join(outdir, "report.md"))
    # Write summary
    with open(os.path.join(outdir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    return outdir
