---
name: sn-search-image
description: >
  当用户需要sensenovasnsearchimage时使用。
  提供专业的设计/内容/分析能力，支持定制化输出。
  不要用于：无关场景。
  触发词：图片搜索、搜图、图片检索、以图搜图
metadata: {"openclaw":{"requires":{"bins":["python3"],"env":["SERPER_API_KEY"]},"primaryEnv":"SERPER_API_KEY"}}
triggers:
  - 图片搜索
  - 搜图
  - 图片检索
  - 以图搜图
tags:
  - sensenova-sn-search-
  - sn

---

# Serper Image Search

Use this skill to search for candidate images via Serper.dev.

## Commands

Standard image search:

```bash
python3 {baseDir}/scripts/serper_image_search.py "QUERY" --num 10
```

Image URLs only:

```bash
python3 {baseDir}/scripts/serper_image_search.py "QUERY" --num 10 --image-urls-only --limit 5
```

Page URLs only:

```bash
python3 {baseDir}/scripts/serper_image_search.py "QUERY" --num 10 --page-urls-only --limit 5
```

Raw JSON:

```bash
python3 {baseDir}/scripts/serper_image_search.py "QUERY" --num 10 --json
```

Save raw JSON to a file for later inspection:

```bash
python3 {baseDir}/scripts/serper_image_search.py "QUERY" --num 10 --save-json /tmp/serper-images.json
```

## Important

- This skill only performs image search and returns candidate result metadata.
- Run the command directly as shown above.
- Do not wrap it with `cd`, shell pipes, `python -c`, here-docs, or output redirection tricks.
- Use `--gl` and `--hl` when you need country or language bias.
