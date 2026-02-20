#!/usr/bin/env python3
"""Interactive agent chat TUI with word-wrapped I/O.

Uses prompt_toolkit for word-wrapped input (no mid-word breaks)
and textwrap for word-wrapped output. Falls back gracefully if
prompt_toolkit is not installed.
"""

import argparse
import os
import subprocess
import sys
import textwrap
import shutil

def parse_args():
    p = argparse.ArgumentParser(description="Talk to any OpenClaw agent from your terminal.")
    p.add_argument("-a", "--agent", default="main", help="Agent name (default: main)")
    p.add_argument("-s", "--server", default="localhost", help="SSH host (default: localhost)")
    p.add_argument("-c", "--color", default="d97757", help="Hex color for agent (default: d97757)")
    p.add_argument("-n", "--name", default=None, help="Display name (default: agent name)")
    p.add_argument("--no-tag", action="store_true", help="Don't prepend [terminal] to messages")
    return p.parse_args()

def hex_to_ansi(hex_color):
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"\033[38;2;{r};{g};{b}m"

def get_width():
    return shutil.get_terminal_size().columns

def wrap_text(text):
    """Word-wrap text to terminal width."""
    width = get_width()
    lines = []
    for paragraph in text.split('\n'):
        if not paragraph.strip():
            lines.append('')
            continue
        wrapped = textwrap.wrap(paragraph, width=width - 4,
                                break_long_words=False,
                                break_on_hyphens=False)
        lines.extend(wrapped if wrapped else [''])
    return lines

def send_message(msg, agent, server, openclaw, remote_path, tag):
    """Send message to agent via OpenClaw gateway."""
    if tag:
        msg = f"[terminal] {msg}"
    escaped = msg.replace("'", "'\\''")

    if server == "localhost":
        cmd = [openclaw, "agent", "--agent", agent, "--message", msg]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return f"(error: {e})"
    else:
        if remote_path:
            cmd = f"{remote_path} {openclaw} agent --agent {agent} --message '{escaped}'"
        else:
            cmd = f"{openclaw} agent --agent {agent} --message '{escaped}'"
        try:
            result = subprocess.run(
                ["ssh", server, cmd],
                capture_output=True, text=True, timeout=120
            )
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            return "(timeout — check connection)"

def main():
    args = parse_args()
    label = args.name or args.agent
    agent_color = hex_to_ansi(args.color)
    openclaw = os.environ.get("OPENCLAW", "openclaw")
    openclaw_dir = os.path.dirname(openclaw)
    remote_path = f"PATH={openclaw_dir}:$PATH" if openclaw_dir and openclaw_dir != "." else ""

    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

    print(f"{agent_color}{BOLD}{label}{RESET} {DIM}— terminal{RESET}")
    print(f"{DIM}Type your message and press Enter. Ctrl+C or Ctrl+D to exit.{RESET}")
    print()

    # Try prompt_toolkit for word-wrapped input
    pt_session = None
    pt_style = None
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.styles import Style
        pt_session = PromptSession()
        pt_style = Style.from_dict({'green': '#00aa00'})
    except ImportError:
        pass

    while True:
        try:
            if pt_session:
                msg = pt_session.prompt(
                    [('class:green', 'you → ')],
                    style=pt_style,
                ).strip()
            else:
                msg = input(f"\033[32myou → \033[0m").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not msg:
            continue

        if msg in ("quit", "exit", "bye"):
            print(f"{DIM}See you later.{RESET}")
            break

        print()
        response = send_message(msg, args.agent, args.server, openclaw, remote_path, not args.no_tag)
        if response:
            lines = wrap_text(response)
            for i, line in enumerate(lines):
                if i == 0:
                    print(f"{agent_color}{label} →{RESET} {line}")
                else:
                    print(f"    {line}")
        else:
            print(f"{DIM}(no response — check connection){RESET}")
        print()

if __name__ == "__main__":
    main()
