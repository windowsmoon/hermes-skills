---
name: sn-ppt-doctor
description: >
  当用户需要sensenovasnpptdoctor时使用。
  提供专业的设计/内容/分析能力，支持定制化输出。
  不要用于：无关场景。
  触发词：PPT诊断、PPT问题修复、PPT检查、PPT优化
metadata:
  project: SenseNova-Skills
  tier: aux
  category: diagnostic
  user_visible: true
triggers:
  - "sn-ppt-doctor"
  - "ppt 体检"
tags:
  - sensenova-sn-ppt-doc
  - sn

---

# sn-ppt-doctor

## When to use

- Before the first time you use `sn-ppt-entry` / `sn-ppt-creative` / `sn-ppt-standard`, to verify env is wired
- After you change `.env`, to confirm
- When `sn-ppt-entry` reports missing-env error and tells you to come here

## Hard checks (must pass before sn-ppt-entry can run)

1. Text chat API key is available via `SN_TEXT_API_KEY`, shared `SN_CHAT_API_KEY`, or global `SN_API_KEY`
2. Vision chat API key is available via `SN_VISION_API_KEY`, shared `SN_CHAT_API_KEY`, or global `SN_API_KEY`
3. Image generation API key is available via `SN_IMAGE_GEN_API_KEY` or global `SN_API_KEY`
4. `sn-image-base` is discoverable and `sn_agent_runner.py --help` works (auto-resolved as a sibling skill under the same `skills/` directory; `SN_IMAGE_BASE` only needed for non-standard layouts)
5. `node --version` >= 18

## Soft checks (warnings only)

- `$(pwd)/ppt_decks/` creatable and writable (deck_dir parent; fixed — not configurable via env)
- `sn-ppt-standard/scripts/export_pptx/node_modules` exists (run `npm install` on first use otherwise)
- Optional env vars (`SN_IMAGE_GEN_*`, `SN_CHAT_*`, `SN_TEXT_*`, `SN_VISION_*`) — displays current value or "unset"
- `pypdf` / `python-docx` Python deps for doc parsing in sn-ppt-entry

## Invocation

Single-file entry; no package imports, no `-m`, no `PYTHONPATH` needed.

```bash
python $SKILL_DIR/ppt_doctor/check_environment.py                      # interactive
python $SKILL_DIR/ppt_doctor/check_environment.py --non-interactive
python $SKILL_DIR/ppt_doctor/check_environment.py --env-path /custom/.env
```

When used inside OpenClaw, `/skill sn-ppt-doctor` runs the same entry.

## Output

Plain text report — one line per check — then a summary. On any hard-check failure, enters interactive mode to fill `.env` (unless `--non-interactive`).

## Does NOT

- Modify `sn-image-*` skills or their `.env`
- Install packages automatically (prints install commands instead)
- Run any PPT pipeline
