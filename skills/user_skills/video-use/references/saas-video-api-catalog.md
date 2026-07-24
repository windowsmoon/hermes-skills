# SaaS Video Tools — API / CLI / Automation Catalog

## Purpose

This file catalogs commercial/SaaS video editing and generation tools by their programmatic interface capabilities (REST API, CLI, SDK, MCP). Use it when a session needs to decide whether an AI agent can call a given video tool, or when choosing between cloud API and local open-source approaches.

Research compiled July 2026. Verify current status before depending on a tool.

---

## Quick Reference

| Tool | Has API? | Can Agent Call? | Best For | Notes |
|------|----------|----------------|----------|-------|
| **Synthesia** | ✅ Full REST API | ✅ Yes | AI avatar video generation, text→video, dubbing | docs.synthesia.io. Create/list videos, templates, webhooks, assets. |
| **Runway** | ✅ Full REST API + SDKs | ✅ Yes | AI video generation, editing, workflows | dev.runwayml.com. Python + Node SDKs. Gen-4.5, Aleph 2.0, Seedance 2.0. |
| **OpusClip** | ⚠️ Limited (Pro) / Custom (Business) | ⚠️ Conditional | Long→short video clipping, viral clip extraction | "Limited API Access" on Pro ($29/mo). Requires sales contact for full API. |
| **NemoVideo** | ❓ Planned (nav link exists, 500 error) | ❌ No | AI video editing agent (chat-based) | Consumer product. API nav link returns 500 — likely in development. |
| **Descript** | ❌ No | ❌ No | Text-based video/audio editing | No public API, SDK, or developer docs. Closed-source desktop app. |
| **CapCut / 剪映** | ❌ No | ❌ No | Mobile/desktop video editing | No official API. The "capcut-agent" GitHub project does not exist. |
| **InVideo** | ❌ No | ❌ No | AI video generation (web-based) | No public API. /developers returns 404. |
| **OpenCut** | ❌ No | ❌ No | Open-source CapCut alternative (76k★) | GUI-only desktop app (Electron/Tauri). No CLI, no API, no headless mode. |
| **CueCut** | — | — | Unknown | Tool does not appear to exist or is extremely obscure. |
| **Video Agent (open source)** | ❌ No | ❌ No | N/A | No specific popular project by this name. Closest is OpenCut (GUI-only). |

---

## Detailed Tool Profiles

### 1. Synthesia — Full REST API ✅

- **URL:** docs.synthesia.io
- **Auth:** API key via Bearer token
- **API Endpoints:**
  - `POST /v2/videos` — Create a video (text/script → video with avatar)
  - `GET /v2/videos/:id` — Retrieve video status/download URL
  - `GET /v2/videos` — List all videos
  - `DELETE /v2/videos/:id` — Delete a video
  - `POST /v2/templates/:id/videos` — Create video from template
  - `GET /v2/templates` — List templates
  - `POST /v2/dubbing` — Create dubbing project
  - `POST /v2/webhooks` — Create webhook (for async completion notifications)
  - `POST /v2/assets` — Upload media assets
- **SDKs:** None official, but REST API is standard HTTP/JSON — callable via cURL, Python requests, fetch, etc.
- **Agent-ready:** Yes. Full CRUD, async with webhooks, media upload support.
- **Limitations:** Video generation, not traditional timeline editing. No multi-track, no cuts/transitions.

### 2. Runway — Full REST API + SDKs ✅

- **URL:** dev.runwayml.com
- **Auth:** API key
- **SDKs:** Python (`@runwayml/sdk`), Node.js
- **Models available via API:**
  - **Gen-4.5** — Balanced everyday video generation (720p, up to 10s, $0.12/s)
  - **Aleph 2.0** — Precise video editing (matches input resolution, up to 30s, $0.28/s)
  - **Seedance 2.0** — Reference-rich 4K generation (up to 15s, from $0.36/s)
  - **Gemini Omni Flash** — Multi-shot cinematic sequences (up to 10s, $0.10/s)
- **Capabilities:** text→video, image→video, video→video editing, image generation
- **Agent-ready:** Yes. Full SDK, async task-based API, webhook support.
- **Limitations:** Generation/edit, not traditional timeline editing. No multi-track.

### 3. OpusClip — Limited API Access ⚠️

- **URL:** opus.pro
- **Pricing:**
  - Pro ($29/mo): "Limited API Access"
  - Business (custom): "API & custom integrations"
- **Public API docs:** None found. Requires sales contact for Business plan.
- **Agent-ready:** Conditional — only on paid plans, with unclear API surface.
- **Best for:** Long-form video → short clips, virality scoring, auto-captions.

### 4. NemoVideo — API Planned ❓

- **URL:** nemovideo.com
- **Status:** Has an "API" link in the main navigation, but returns HTTP 500. No public docs.
- **Product:** Consumer AI video editing agent (chat-based). "Just chat what you want."
- **Agent-ready:** Not yet. Monitor for API launch.

### 5. Descript — No Public API ❌

- **URL:** descript.com
- **Status:** Closed-source desktop app. No public API, SDK, or developer portal.
- **Integrations:** Zapier connector exists (limited), but no programmatic video editing.
- **Agent-ready:** No. No way to call Descript programmatically.

### 6. CapCut / 剪映 — No Official API, but Rich Community Ecosystem ⚠️

- **URL:** capcut.com / capcut.cn
- **Status:** No official REST API, SDK, or developer platform from ByteDance. The Volcengine (火山引擎) "Intelligent Video Creation SDK" exists but is enterprise-only (requires business contact).
- **Community projects:** Multiple mature open-source tools exist that work by directly manipulating CapCut/剪映 draft files (JSON-based project files stored locally). See the companion reference `references/capcut-automation.md` for the full catalog of tools, their capabilities, and limitations.
- **Key tools summarized:**
  - **pyJianYingDraft** (4k★) — Python library to generate/edit drafts programmatically. `pip install pyJianYingDraft`. Supports video/audio/images/text/effects/keyframes/masks/transitions.
  - **capcut-cli** (178★) — Node.js CLI that reads/writes drafts directly. `npm install -g capcut-cli`. Supports subtitles, trimming, speed, effects, captions, translation, templates, serve mode for n8n/Coze.
  - **capcut-mate** (1.4k★) — FastAPI REST API service with Docker deployment. Has a Coze plugin. Supports cloud rendering. Full OpenAPI docs.
  - **jianying-editor-skill** (2.5k★) — Hermes/Claude Code skill for AI-agent-driven剪映 editing (uses pyJianYingDraft under the hood).
  - **capcut-tts-api** (218★) — Pure Python CapCut TTS/STT client.
  - **pyCapCut** (596★) — International (CapCut) version of pyJianYingDraft.
- **Caveat:** Newer CapCut/剪映 versions (v7+) may encrypt `draft_content.json`, requiring a `fallback_loader`. Auto-export via UI automation is broken on v7+. Final video export still requires manual action in the app.
- **Agent-ready:** ⚠️ Conditionally — via the community tools, but the last step (export to video) is manual for newer versions.

### 7. InVideo — No Public API ❌

- **URL:** invideo.io
- **Status:** Consumer web app. `/developers` returns 404. No developer portal.
- **Agent-ready:** No.

### 8. OpenCut (Open-Source CapCut Alternative) — GUI Only ❌

- **URL:** github.com/OpenCut-app/OpenCut
- **Stars:** ~76k
- **Status:** Open-source, MIT license. Desktop app (Electron/Tauri). No CLI, no API, no headless mode.
- **Agent-ready:** No. GUI-only.

### 9. CueCut — Not Found

- **Status:** No results found in any search engine or GitHub. Tool may not exist or is extremely obscure.

### 10. Video Agent (Open Source) — Not Found

- **Status:** No specific popular open-source project by this name. The term is ambiguous. Closest projects are OpenCut (GUI editor) and auto-editor (CLI silence removal), but neither is called "Video Agent."

---

## MCP Servers for Video Editing

| MCP Server | Backend | Status | Notes |
|------------|---------|--------|-------|
| **mcp-ffmpeg** | FFmpeg | Community | Trimming, transitions, filters, color grading |
| **mcp-moviepy** | MoviePy | Community | Programmatic editing, compositing |
| **mcp-video-edit** | FFmpeg | Community | General video editing operations |
| **mcp-editly** | Editly | Community | Node.js-based transitions pipeline |
| **mcp-shotstack** | Shotstack API | Community | Cloud-based editing (commercial) |

All are early-stage community projects. Search GitHub for `mcp video` or `mcp ffmpeg` for latest repos.
No dedicated MCP server for Synthesia, Runway, or other SaaS video tools was found in public registries.

---

## Open-Source CLI / Programmatic Alternatives (Best for Agent Automation)

When SaaS APIs are not the right fit, these open-source tools are all agent-callable:

| Tool | Type | Install | Best For |
|------|------|---------|----------|
| **FFmpeg** | CLI (native) | `apt install ffmpeg` / `winget install ffmpeg` | Every video operation — trim, concat, transcode, filter, overlay, subtitle |
| **MoviePy** | Python library | `pip install moviepy` | Programmatic video editing in Python — cuts, compositing, effects, text |
| **auto-editor** | Python CLI | `pip install auto-editor` | Automatic silence removal, motion-based cutting |
| **Remotion** | npm package | `npm install remotion` | React-based programmatic video creation |
| **editly** | npm CLI | `npm install -g editly` | JSON-config-based video editing with transitions |
| **videogrep** | Python CLI | `pip install videogrep` | Search video transcripts and create supercuts |
| **ffmpeg-python** | Python library | `pip install ffmpeg-python` | Pythonic wrapper around FFmpeg |

---

## Decision Framework

When choosing a video automation approach for an AI agent:

1. **Need traditional editing (cuts, multi-track, transitions)?** → Open-source CLI/Python tools (FFmpeg + MoviePy + auto-editor + Remotion). No SaaS API does this well yet.
2. **Need AI avatar video generation?** → Synthesia API (best in class for avatars).
3. **Need AI video generation/editing (text→video, image→video)?** → Runway API (best model selection + SDK).
4. **Need long→short clipping with AI?** → OpusClip (conditional API access, or build with FFmpeg + Whisper + auto-editor).
5. **Need a dedicated MCP video server?** → mcp-ffmpeg or mcp-moviepy (community, early-stage).