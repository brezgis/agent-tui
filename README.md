# agent-tui

Talk to any [OpenClaw](https://github.com/openclaw/openclaw) agent from your terminal. Local or remote via SSH.

Three modes, auto-selected by available dependencies:

| Mode | Dependency | Features |
|------|-----------|----------|
| **Textual** (best) | `textual` | Rich TUI, Catppuccin Mocha theme, spinner, word wrap |
| **prompt_toolkit** | `prompt_toolkit` | Word-wrapped input/output |
| **Bash** (fallback) | none | Basic readline input, `fold -s` output |

## Quick Start

```bash
# Install for best experience
pip install textual

# Local agent
./agent-tui.sh

# Remote agent via SSH
./agent-tui.sh -a main -s myserver

# Custom display name
./agent-tui.sh -a tutor -n rook
```

## Options

```
  -a, --agent NAME      Agent name (default: main)
  -s, --server HOST     SSH host for remote OpenClaw (default: localhost)
  -c, --color HEX       Hex color for agent responses (bash/pt mode, default: d97757)
  -n, --name LABEL      Display name for the agent (default: agent name)
  --no-tag              Don't prepend [terminal] to messages
  -h, --help            Show this help
```

## How It Works

Messages are sent to an OpenClaw agent via `openclaw agent --message`. In remote mode, this runs over SSH. Messages get a `[terminal]` prefix so agents can adjust formatting (skip markdown, keep things concise).

The Textual TUI (`agent-tui-textual.py`) provides:
- Catppuccin Mocha dark theme
- Animated spinner with rotating status messages while waiting
- Rich text formatting with word wrap
- Multi-line input (Shift+Enter for newlines)
- Works over SSH/tmux

## Install

```bash
git clone https://github.com/brezgis/agent-tui.git
cd agent-tui
chmod +x agent-tui.sh agent-tui-textual.py agent-tui.py

# For the best experience:
pip install textual

# Or for basic word-wrapped input:
pip install prompt_toolkit
```

## Environment

| Variable | Description |
|----------|-------------|
| `OPENCLAW` | Path to openclaw binary (default: `openclaw`). Set this if openclaw isn't in your PATH, e.g. when installed via nvm. |
| `AGENT` | Default agent name (overridden by `-a`) |
| `SERVER` | Default SSH host (overridden by `-s`) |

## Tips

```bash
# Chat with your main agent on a remote server
alias chat="./path/to/agent-tui.sh -a main -s myserver"

# Chat with a tutor agent
alias tutor="./path/to/agent-tui.sh -a tutor -s myserver -n rook"
```

## License

MIT
