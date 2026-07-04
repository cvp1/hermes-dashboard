# Hermes Dashboard

A portable, Linear-inspired dashboard for your [Hermes AI agent](https://hermes-agent.nousresearch.com/).
Auto-discovers your installed skills, configurable services, and runs entirely from your home directory.

## Quick Start

```bash
git clone <this-repo>
cd hermes-dashboard
cp _lib/services.json.example _lib/services.json  # customize your services
echo "admin:sekret" > ~/.key/dash-auth             # or set DASH_USER/DASH_PASS
python3 _lib/dashboard.py
```

Open **http://localhost:8080** in your browser.

## Configuration

### Services
Edit `_lib/services.json` to add/remove service cards. Format:
```json
[
  {"label":"My Service", "href":"http://localhost:3000/", "desc":"What it does", "ico":"📊", "ext":"↗"}
]
```

### Authentication
Three ways, checked in order:
1. **`DASH_USER` / `DASH_PASS`** env vars
2. **`DASH_AUTH_FILE`** env var pointing to a `user:password` file
3. **`~/.key/dash-auth`** — default fallback

### Skill Icons
Customize emoji by creating `~/.hermes/skills/.emoji.json`:
```json
{"backup":"💾", "triage":"📥"}
```

## What It Shows

- **Sidebar** — Auto-discovered skills from `~/.hermes/skills/`
- **Status** — Hermes daemons, Ollama, MCP servers, cron jobs, events, costs
- **Search** — Full-text search against Hermes knowledge index
- **Triage** — Classify new emails via local LLM
- **Services** — Your pinned service links
- **Terminals** — Embedded ttyd sessions (bash + hermes)

## Dependencies

- Python 3.10+
- [Hermes Agent](https://hermes-agent.nousresearch.com/) (for skills & MCP)
- Optional: ttyd for embedded terminals
- Optional: Ollama on .21 for local LLM features
