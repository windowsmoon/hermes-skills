# NemoVideo Setup Reference

## Overview
NemoVideo is a pro AI video editing agent. Chat natural language to generate, edit, and export MP4 videos.

## Architecture
```
You ↔ OpenClaw Agent ↔ [SKILL.md] ↔ NemoVideo Backend AI Agent
                           ↕
                    API (SSE + REST)
```

- NemoVideo skill acts as an **interface layer** between OpenClaw and NemoVideo's backend.
- The backend API is **private/internal** — there is no publicly documented REST API for direct use.

## Key URLs
- Website: https://www.nemovideo.com
- GitHub: https://github.com/nemovideo/nemovideo_skills
- API (internal, 500 error on public page): https://www.nemovideo.com/api
- Backend API URL: `https://mega-api-prod.nemovideo.ai`

## Installation Commands

### Option A: Via ClawHub (recommended)
```bash
# Install OpenClaw first (the agent gateway)
curl -fsSL https://openclaw.ai/install.sh | bash        # macOS/Linux/WSL2
# OR
powershell -c "irm https://openclaw.ai/install.ps1 | iex"  # Windows

# Install ClawHub CLI
npm i -g clawhub

# Install NemoVideo skill
clawhub install nemo-video

# Alternative: native OpenClaw command
openclaw skills install nemo-video
```

### Option B: Manual Install
```bash
git clone https://github.com/nemovideo/nemovideo_skills.git
cp -r nemovideo_skills ~/.openclaw/skills/nemo-video
```

## Credentials & Configuration

### Environment Variables (all optional)
| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `NEMO_TOKEN` | No | Auto-generated | 100 free trial credits, 1 token per client per 7 days, expires in 7 days |
| `NEMO_API_URL` | No | `https://mega-api-prod.nemovideo.ai` | Backend API endpoint |
| `NEMO_CLIENT_ID` | No | Auto-generated UUID | Persisted locally |

### Free Trial
- **100 free credits** on first use
- **No signup needed** — auto-creates anonymous account
- When exhausted, register at https://nemovideo.com for more credits

### Paid Plans
| Plan | Price | Credits |
|------|-------|---------|
| Free | $0 | 100 credits |
| Starter | $17.99/mo (annual) | 1,100 credits/month |
| Pro | $34.99/mo (annual) | 2,300+ credits/month |

## Supported Formats
| Type | Formats |
|------|---------|
| Video | mp4, mov, avi, webm, mkv |
| Image | jpg, png, gif, webp |
| Audio | mp3, wav, m4a, aac |

## Usage Examples (chat with agent)
```
"Make me a 10-second sunset timelapse video"
"Add lo-fi background music"
"Put a title 'Golden Hour' at the beginning"
"Upload this video and add captions"
"Export it"
```

## Key Files in Repo
- `SKILL.md` — OpenClaw skill definition (v1.9, MIT license)
- `README.md` — Quick start guide
- `CHANGELOG.md` — Release history
- `VERSION` — Current version
- `scripts/bump-version.sh` — Version management script

## OpenClaw Ecosystem (for context)
- **OpenClaw**: Self-hosted AI agent gateway (open-source, MIT). Installed via one-liner or npm.
- **ClawHub**: Public registry for OpenClaw skills and plugins. Accessible at https://clawhub.ai
- **clawhub CLI**: npm package (`npm i -g clawhub`) for registry-authenticated workflows (install, publish, search, etc.)
- **Native OpenClaw commands**: `openclaw skills install`, `openclaw plugins install`, `openclaw skills search`