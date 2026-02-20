# agent-tui

Talk to any [OpenClaw](https://github.com/openclaw/openclaw) agent from your terminal. Local or remote via SSH.

Word-wrapped input and output — no mid-word breaks.

## Quick Start

```bash
# Local agent
./agent-tui.sh

# Remote agent via SSH
./agent-tui.sh -a main -s myserver

# Custom display name and color
./agent-tui.sh -a tutor -s myserver -n rook -c 36b5a0
```

## Options

```
  -a, --agent NAME      Agent name (default: main)
  -s, --server HOST     SSH host for remote OpenClaw (default: localhost)
  -c, --color HEX       Hex color for agent responses (default: d97757)
  -n, --name LABEL      Display name for the agent (default: agent name)
  --no-tag              Don't prepend [terminal] to messages
  -h, --help            Show this help
```

## How It Works

Messages are sent to an OpenClaw agent via `openclaw agent --message`. In remote mode, this runs over SSH. Messages get a `[terminal]` prefix so agents can adjust formatting (skip markdown, keep things concise).

If [prompt_toolkit](https://python-prompt-toolkit.readthedocs.io/) is installed, the input uses word-level wrapping — long messages wrap at word boundaries as you type, not mid-word. Agent responses are also word-wrapped via `textwrap`.

Without prompt_toolkit, falls back to bash with `read -p` (non-deletable prompt) and `fold -s` (word-wrapped output).

## Install

```bash
git clone https://github.com/brezgis/agent-tui.git
cd agent-tui
chmod +x agent-tui.sh agent-tui.py

# Optional: install prompt_toolkit for word-wrapped input
pip install prompt_toolkit
```

## Environment

| Variable | Description |
|----------|-------------|
| `OPENCLAW` | Path to openclaw binary (default: `openclaw`). Set this if openclaw isn't in your PATH, e.g. when installed via nvm. |

## Tips

Add an alias to your shell config:

```bash
# Chat with your main agent on a remote server
alias chat="./path/to/agent-tui.sh -a main -s myserver -n claude"

# Chat with a tutor agent
alias tutor="./path/to/agent-tui.sh -a tutor -s myserver -n rook -c 36b5a0"
```

## License

MIT
