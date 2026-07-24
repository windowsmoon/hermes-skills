# Tool Capability Verification Methodology

## Why This Document Exists

During the 2026-07-21 session, the user challenged my capability claims for the scraping tool stack. I had mixed three things:
1. Tools I had actually used -> could speak from experience
2. Tools I had only read about -> documentation-based inferences
3. Tools I had only installed -> assumed features based on project name

The user's challenge: "你觉得你那个覆盖能力里面，是真的如你所设想的那样吗？"

## Verification Process (Applied Retroactively)

For each tool, the correct verification method:

| Tool | How to Verify | Status |
|:-----|:-------------|:-------|
| Firecrawl | Already used in pipelines | Used, confirmed |
| Tabbit Browser | Already used in buyin-harvester | Used, confirmed |
| Playwright MCP | `--help` flag, npm registry, README | CLI help check |
| Hermes browser | Direct tool calls | Direct use |
| computer-control-mcp | `--help` + subcommand listing | CLI test |

Key finding: `computer-control-mcp` has built-in RapidOCR PP-OCRv4 (confirmed via runtime log). NO tool has native chart understanding.

## Rule for Future Skill Authoring

Before writing "Tool X has/can Y" in any skill:
1. Check `--help` or subcommand listing
2. Check runtime logs for module loading
3. If uncertain, write "needs verification" as a pitfall
4. Separate "confirmed" vs "inferred" vs "assumed" in capability docs

If you cannot verify, flag it with 未验证 (unverified).
