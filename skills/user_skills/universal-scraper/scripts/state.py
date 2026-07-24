"""
universal_scraper state.py — 采集状态管理
采集去重、进度追踪、翻页控制
"""
import json, hashlib, os
from datetime import datetime

class ScrapeState:
    def __init__(self, state_path):
        self.path = state_path
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "url": "",
            "status": "init",
            "target_urls": [],
            "scraped_urls": {},
            "records": [],
            "seen_hashes": {},
            "page": 0,
            "max_pages": 1,
            "scroll_count": 0,
            "empty_rounds": 0,
            "errors": [],
            "layer": 0,
            "started_at": datetime.now().isoformat(),
            "output_dir": "",
        }

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def url_hash(self, url, content_preview):
        return hashlib.md5((url + content_preview[:50]).encode()).hexdigest()

    def is_duplicate(self, url, content):
        h = self.url_hash(url, content)
        return h in self.data["seen_hashes"]

    def add_record(self, url, content, images=None):
        h = self.url_hash(url, content)
        if h in self.data["seen_hashes"]:
            return False
        record = {
            "page": self.data["page"],
            "url": url,
            "content_preview": content[:200],
            "content_len": len(content),
            "image_count": len(images) if images else 0,
            "images": images or [],
            "timestamp": datetime.now().isoformat(),
        }
        self.data["records"].append(record)
        self.data["seen_hashes"][h] = True
        self.data["scraped_urls"][url] = True
        self.save()
        return True

    def reached_end(self, threshold=2):
        if self.data["empty_rounds"] >= threshold:
            return True
        if self.data["page"] >= self.data["max_pages"]:
            return True
        return False

    def summary(self):
        return {
            "total_urls": len(self.data["target_urls"]),
            "scraped_urls": len(self.data["scraped_urls"]),
            "total_records": len(self.data["records"]),
            "errors": len(self.data["errors"]),
            "layer_used": ["firecrawl", "browser", "computer_control"][self.data["layer"]],
            "pages_traversed": self.data["page"],
        }
