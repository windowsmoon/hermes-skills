# Tool Capability Verification Notes

## Verification Date: 2026-07-21
## Trigger: User corrections about accuracy of capability claims

## Key Findings

1. **No tool has native "chart understanding"** - all screenshots must go through vision_analyze (qwen3-vl-plus)
2. **computer-control-mcp has built-in RapidOCR** (PP-OCRv4 Chinese), but OCR extraction != chart understanding
3. **Hermes browser_vision is the only tool with built-in vision** - others need manual vision_analyze
4. **Firecrawl is for text-heavy public pages** - not good for JS-rendered or login-required sites
5. **computer-control-mcp is last resort** - coordinates-only, no DOM, good for extreme anti-scraping

## Per-Tool Verification

### Firecrawl
- API key configured. Confirmed: returns markdown text, image URLs, supports pagination params
- NOT: JS rendering, screenshots, vision analysis

### Hermes Browser (built-in)
- Direct tool calls. Confirmed: navigate, snapshot, get_images, vision(screenshot+analysis), scroll, click

### Tabbit Browser
- Referenced live usage. Confirmed: navigate, screenshot, text extract, antidetect, scroll/click
- NOT: built-in vision, DOM element location

### Playwright MCP (v0.0.78)
- npm registry + README. Confirmed: navigate, screenshot, click, type, JS, PDF, accessibility tree
- NOT: built-in vision

### computer-control-mcp (v2.1.0)
- Installed + tested. Commands: server, click, type, screenshot(3 modes), list-windows, gui
- Built-in RapidOCR confirmed via runtime log (PP-OCRv4 detection/orientation/recognition models)
- NOT: element-level positioning (coordinates only), chart analysis

### vision_analyze
- Direct call. Confirmed: analyzes any image, understands chart data relationships
- Backend: qwen3-vl-plus

## Principle

Before writing "Tool X has/can Y" in any skill: call/test the tool first, or verify via official docs. Record the method. Flag unverified assumptions.
