# CapCut / 剪映 Automation Reference

## Status Overview

| Aspect | Status |
|--------|--------|
| Official ByteDance REST API | ❌ None exists |
| Official SDK (public) | ❌ None exists |
| Volcengine Video Creation SDK | ⚠️ Enterprise-only (requires business contact) |
| Open-source draft manipulation | ✅ Very mature (multiple projects, 4k★+) |
| Draft file format | ⚠️ Newer v7+ may encrypt `draft_content.json` |
| Automated video export | ❌ Broken on v7+ (UI controls hidden) |

## How It Works

All community tools work by **directly manipulating CapCut/剪映's local project files**. No API calls to ByteDance servers are needed.

### Draft File Structure

CapCut/剪映 stores each project as a directory under:
- **Windows:** `%LOCALAPPDATA%/JianyingPro/Drafts/` or user-configured path
- **macOS:** `~/Movies/JianyingPro/Drafts/`
- **Key files inside a draft directory:**
  - `draft_content.json` — The main timeline/project data (tracks, segments, effects, keyframes)
  - `draft_material.json` — Material references (media files, resources)
  - `draft_audio.json` — Audio-specific data
  - `draft_settings.json` — Project settings (resolution, fps, etc.)
  - `draft_meta.json` — Metadata
  - `draft_timeline.json` or `draft_timeline_*.json` — Timeline mirror files (v8.7+)

### Important Caveat: Newer Versions

CapCut/剪映 v7+ (approximately late 2024 onwards) may encrypt `draft_content.json` using a proprietary format. The open-source tools handle this differently:
- **pyJianYingDraft** supports `fallback_loader` parameter for custom decryption
- **capcut-cli** uses `sync-timelines` command to detect and repair newer timeline formats
- Simple JSON editing may not work on encrypted drafts — you need to use the tools' built-in loaders

## Tool Catalog

### 1. pyJianYingDraft (Python) — ⭐ 4,000 stars — MOST MATURE

**Repository:** https://github.com/GuanYixuan/pyJianYingDraft
**Install:** `pip install pyJianYingDraft`
**License:** Apache 2.0
**Last update:** Active (2 weeks ago)

**Capabilities:**
- ✅ Video/Image clips with time control, cropping, scaling
- ✅ Audio clips with fade in/out, volume control
- ✅ Keyframes (position, scale, rotation, opacity)
- ✅ Masks (various shapes)
- ✅ Chroma key (green screen)
- ✅ Video background fill
- ✅ Blend modes
- ✅ Stickers
- ✅ Effects (scene effects, audio effects, sound-to-melody)
- ✅ Filters (per-segment and per-track)
- ✅ Transitions
- ✅ Text with full styling (font, color, stroke, shadow, background, bubble, fancy text)
- ✅ Text animations (entrance/exit/loop)
- ✅ SRT subtitle import
- ✅ Text auto-wrap
- ✅ Template mode: load existing draft as template, replace materials/text
- ✅ Import tracks from other drafts
- ✅ Extract material metadata (resource IDs for stickers, bubbles, fancy text)
- ❌ Auto-export to video: Only works on JianYing v6 and below (uses UI automation via `uiautomation` library, Windows only)
- ⚠️ Template mode: Newer drafts may need `fallback_loader` for encrypted files

**Compatibility:**
- JianYing 5.9: ✅ Full support
- JianYing 10.8 (newer): ✅ Most features, but template loading needs `fallback_loader`
- Auto-export: ❌ Broken on v7+
- Linux/macOS: Can generate drafts, but cannot auto-export (needs Windows)

### 2. capcut-cli (Node.js) — ⭐ 178 stars — BEST CLI

**Repository:** https://github.com/renezander030/capcut-cli
**Install:** `npm install -g capcut-cli`
**License:** MIT
**Last update:** Active (yesterday)

**Capabilities:**
- ✅ Inspect drafts (info, tracks, materials, segments, texts)
- ✅ Create drafts (init, quickstart, compile from JSON spec)
- ✅ Add video/audio/text (supports Wikimedia URLs with license checks)
- ✅ Edit: trim, speed, volume, transitions, masks, text/image animations, easing curves
- ✅ Subtitles & captions: generate (via Whisper), import SRT, export SRT/VTT (line + word-level)
- ✅ Translation: multi-language draft clone
- ✅ Effects: SFX, chroma key
- ✅ Long-form → short: cut, detect-scenes (via FFmpeg)
- ✅ Templates: apply, extract, make-preset (portable text-style presets)
- ✅ Automation: `serve` mode (JSONL job runner from stdin, compatible with n8n/Make/Coze)
- ✅ Timeline mirror repair for CapCut 8.7+ (`sync-timelines`)
- ✅ Keyframe easing (CapCut-native)
- ✅ Lint + fix (`lint --fix`)
- ✅ Duplicate segment onto overlay track
- ✅ Read + edit source-material crop
- ✅ Per-word keyword emphasis and color cycling for captions
- ✅ Claude Code plugin integration
- ✅ Render: low-res preview via FFmpeg (not final CapCut render)

**Supports both namespaces:** `--jianying` flag for JianYing enum values, otherwise CapCut defaults.

**Prerequisites:** Node.js 18+, optional: FFmpeg (for render/preview), Whisper (for caption), ffprobe (for media metadata).

### 3. capcut-mate (FastAPI) — ⭐ 1,392 stars — BEST FOR COZE/n8n INTEGRATION

**Repository:** https://github.com/Hommy-master/capcut-mate
**Install:** Docker or `uv sync`
**Last update:** Very active (25 minutes ago)
**License:** Open source

**Capabilities:**
- Full REST API (FastAPI, auto-generated OpenAPI docs at `/docs`)
- Create/save/get drafts
- Add videos, images, audios, stickers, captions, text styles
- Effects, keyframes, masks
- Cloud rendering (generate final video from draft)
- Coze plugin (one-click import from `openapi.yaml`)
- Docker deployment
- 572 commits, very actively maintained

### 4. jianying-editor-skill — ⭐ 2,502 stars — BEST FOR AI AGENTS

**Repository:** https://github.com/luoluoluo22/jianying-editor-skill
**Last update:** Active (last month, 111 commits)

This is an **AI Agent skill** (for Hermes, Claude Code, Cursor, etc.) that provides:
- Complete prompts, rules, scripts, and references for AI agents to drive剪映 editing
- Uses `pyJianYingDraft` as the underlying draft engine
- Includes agent workflow documentation, examples, and test suite
- Designed specifically for AI-agent-driven video editing

### 5. pyCapCut — ⭐ 596 stars — CapCut (International) Version

**Repository:** https://github.com/GuanYixuan/pyCapCut
**Status:** International version of pyJianYingDraft. Less mature (18 commits, last update 10 months ago) but purpose-built for the international CapCut product.

### 6. capcut-tts-api — ⭐ 218 stars — TTS/STT ONLY

**Repository:** https://github.com/K07VN/capcut-tts-api
**Status:** Pure Python client for CapCut's Text-to-Speech and Speech-to-Text services. No native libraries needed. Implements request construction, payload signing, upload signing, and VOD authorization in pure Python.

## Workflow Patterns

### Pattern A: Code-Only (Draft Generation)
```
Python/pyJianYingDraft → generate draft JSON → save to drafts folder
→ open CapCut/剪映 manually → review → export manually
```

### Pattern B: CLI Pipeline
```
capcut-cli init → capcut add-video → capcut caption → capcut render
→ open CapCut/剪映 → final export
```

### Pattern C: REST API + Automation
```
capcut-mate (Docker) → create_draft API → add_videos API → gen_video API
→ integrates with Coze/n8n
```

### Pattern D: AI Agent Driven
```
AI Agent → jianying-editor-skill → pyJianYingDraft → draft files
→ CapCut/剪映 → manual export
```

## Key Limitations

1. **No official API** — All tools are reverse-engineering the draft format. Breaking changes on CapCut updates can happen.
2. **No programmatic export on v7+** — The final video export step still requires manual action in the app.
3. **Encrypted drafts** — Newer versions may encrypt `draft_content.json`. Tool support varies.
4. **SVIP features** — While the tools can reference any CapCut resource (fonts, effects, stickers), using SVIP-only resources requires the user to have SVIP activated in their CapCut account.
5. **Windows dependency** — `pyJianYingDraft`'s auto-export and `capcut-mate`'s cloud rendering are Windows-only.

## MCP Integration

No dedicated MCP server for CapCut exists yet. But possibilities:
- **capcut-cli** has a `.claude-plugin/` directory — can be used as a Claude Code plugin
- **capcut-mate** provides REST API — can be wrapped as an MCP server via `mcp-proxy` or similar
- Custom MCP server could be built wrapping `pyJianYingDraft` + `capcut-cli` capabilities

## Quick Decision Guide

| Your need | Best tool |
|-----------|-----------|
| Generate drafts in Python | pyJianYingDraft |
| CLI tool for editing drafts | capcut-cli |
| REST API + Coze integration | capcut-mate |
| AI agent driving剪映 | jianying-editor-skill |
| CapCut (international) draft generation | pyCapCut |
| TTS/STT audio generation | capcut-tts-api |
| Batch processing / automation pipeline | capcut-mate + capcut-cli serve mode |
| Integration with n8n/Make | capcut-cli serve or capcut-mate API |