# openclaw-tui

Talk to your [OpenClaw](https://github.com/openclaw/openclaw) agent from a terminal. That's it.

Works with local instances or remote servers over SSH. Custom colors. No dependencies beyond bash and (optionally) SSH.

## Why

Because sometimes you want to talk to your agent without opening Discord, or a browser, or anything else. Just a terminal and a prompt.

## Install

```bash
git clone https://github.com/brezgis/openclaw-tui.git
cd openclaw-tui
chmod +x oc-chat.sh
```

## Usage

```bash
# Talk to your main agent (local OpenClaw)
./oc-chat.sh

# Talk to an agent on a remote server via SSH
./oc-chat.sh -a main -s myserver

# Talk to a specific agent with a custom color
./oc-chat.sh -a tutor -s myserver -c 36b5a0

# Custom display name
./oc-chat.sh -a main -n claude -c d97757
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `-a, --agent NAME` | OpenClaw agent name | `main` |
| `-s, --server HOST` | SSH host (or `localhost` for local) | `localhost` |
| `-c, --color HEX` | Hex color for agent label (no `#`) | `d97757` |
| `-n, --name LABEL` | Display name in the chat | agent name |
| `--no-tag` | Don't prepend `[terminal]` to messages | off |
| `-h, --help` | Show help | |

### Aliases

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Local agent
alias chat="bash ~/path/to/oc-chat.sh"

# Remote agent with custom name and color
alias cb="bash ~/path/to/oc-chat.sh -a main -s north -n claude -c d97757"

# Remote tutor
alias tutor="bash ~/path/to/oc-chat.sh -a tutor -s north -c 36d9a0"
```

## Local vs Remote

**Local mode** (default): OpenClaw runs on your machine. The script calls `openclaw` directly.

```bash
./oc-chat.sh -a main
```

**Remote mode**: OpenClaw runs on another machine (home server, VPS, etc.). The script sends commands over SSH.

```bash
./oc-chat.sh -a main -s myserver
```

If OpenClaw is installed via nvm or a non-standard path on the remote machine, set `OPENCLAW` so the SSH session can find it:

```bash
export OPENCLAW=/home/user/.nvm/versions/node/v22.22.0/bin/openclaw
./oc-chat.sh -a main -s myserver
```

This is necessary because non-interactive SSH doesn't load `.bashrc` or nvm, so `openclaw` won't be in PATH. The script uses `OPENCLAW` to both locate the binary and set the remote PATH automatically.

## The `[terminal]` Tag

By default, every message is prefixed with `[terminal]`. This lets your agent detect it's being accessed from a terminal and adjust formatting — no markdown (renders as raw `**asterisks**`), shorter responses, plain text emphasis.

Add something like this to your agent's system prompt:

```
Messages prefixed with [terminal] come from a terminal chat.
Use plain text only — no markdown, no bold, no headers.
Keep responses concise; the pane is narrow.
```

Disable with `--no-tag` if you don't want this behavior.

## Requirements

- bash
- [OpenClaw](https://github.com/openclaw/openclaw) (local or on a remote server)
- SSH (for remote mode)
- A terminal that supports true color (most modern terminals do — iTerm2, Alacritty, Kitty, Windows Terminal, etc.)

## License

[MIT](LICENSE)
