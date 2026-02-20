#!/usr/bin/env python3
"""Textual TUI chat app for OpenClaw agents.

A rich terminal UI with Catppuccin Mocha theme, spinner animation,
word-wrapped output, and SSH remote support.

Usage:
    python3 agent-tui-textual.py [agent] [server]

    agent   — Agent name (default: main, or $AGENT env var)
    server  — SSH host (default: localhost, or $SERVER env var)

Environment:
    OPENCLAW  — Path to openclaw binary (auto-detected if unset)
    AGENT     — Default agent name
    SERVER    — Default SSH host
"""

import asyncio
import os
import random
import sys
import shlex

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import RichLog, TextArea, Static
from textual.containers import Vertical
from textual.timer import Timer
from rich.text import Text


AGENT = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("AGENT", "main")).lower()
DISPLAY_NAME = AGENT.capitalize()
SERVER = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("SERVER", "localhost")

# Accent color — lavender for neutral agent chat
ACCENT = "#b4befe"

THINKING_MESSAGES = [
    # General
    "pondering",
    "consulting the oracle",
    "reading the room",
    "connecting the dots",
    "mulling it over",
    "chewing on that",
    "letting it marinate",
    "thinking out loud",
    "weighing options",
    "gathering thoughts",
    "considering the angles",
    "piecing it together",
    "running the numbers",
    "sleeping on it (briefly)",
    # CS-flavored
    "compiling thoughts",
    "traversing the tree",
    "searching the heap",
    "resolving dependencies",
    "optimizing",
    "dereferencing pointers",
    "unwinding the stack",
    "consulting the docs",
    "running the garbage collector",
    "rebalancing the tree",
    "checking edge cases",
    "reducing to base case",
    "hashing it out",
    "building the parse tree",
    "evaluating the expression",
    "sorting thoughts in O(n log n)",
    "awaiting the future",
]


def _find_openclaw(server: str):
    """Find openclaw binary — check env, common nvm paths, then bare name."""
    if os.environ.get("OPENCLAW"):
        return os.environ["OPENCLAW"]
    if server != "localhost":
        return "openclaw"
    import shutil
    if shutil.which("openclaw"):
        return "openclaw"
    import glob
    for p in glob.glob(os.path.expanduser("~/.nvm/versions/node/*/bin/openclaw")):
        return p
    return "openclaw"


OPENCLAW = _find_openclaw(SERVER)
REMOTE_PATH = f"PATH={os.path.dirname(OPENCLAW)}:$PATH" if OPENCLAW != "openclaw" else "PATH=$PATH"


def build_command(message: str) -> list[str]:
    """Build the command to send a message to an agent."""
    escaped = message.replace("'", "'\\''")
    payload = f"[terminal] {escaped}"
    if SERVER == "localhost":
        return [OPENCLAW, "agent", "--agent", AGENT, "--message", payload]
    else:
        remote_cmd = f"{REMOTE_PATH} {OPENCLAW} agent --agent {AGENT} --message {shlex.quote(payload)}"
        return ["ssh", SERVER, remote_cmd]


class ChatInput(TextArea):
    """Multi-line input with Enter to send."""

    BINDINGS = [
        Binding("enter", "submit", "Send", show=False),
    ]

    def action_submit(self) -> None:
        text = self.text.strip()
        if text:
            self.app.send_message(text)
            self.clear()

    def _on_key(self, event) -> None:
        if event.key == "enter":
            event.prevent_default()
            event.stop()
            self.action_submit()
        elif event.key in ("shift+enter", "ctrl+enter"):
            self.insert("\n")


class ChatApp(App):
    """OpenClaw agent chat TUI."""

    CSS_PATH = "agent-tui.tcss"
    TITLE = f"{DISPLAY_NAME} — Chat"
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=True),
        Binding("ctrl+d", "quit", "Quit", show=False),
    ]

    _spinner_frames = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    _spinner_index = 0
    _spinner_timer: Timer | None = None
    _thinking_msg = ""

    def compose(self) -> ComposeResult:
        yield Static(
            f"[bold {ACCENT}]{DISPLAY_NAME}[/bold {ACCENT}] [dim]— Chat[/dim]\n"
            f"[dim]Type your message and press Enter. Ctrl+C or Ctrl+D to exit.[/dim]",
            id="header",
        )
        with Vertical():
            yield RichLog(id="chat", wrap=True, highlight=False, markup=False)
            yield Static("", id="spinner")
            yield ChatInput(id="input")

    def on_mount(self) -> None:
        self.query_one("#input").focus()

    def _start_spinner(self) -> None:
        self._spinner_index = 0
        self._thinking_msg = random.choice(THINKING_MESSAGES)
        spinner = self.query_one("#spinner", Static)
        spinner.update(f"  [dim]{self._spinner_frames[0]} {self._thinking_msg}...[/dim]")
        spinner.display = True
        self._spinner_timer = self.set_interval(0.08, self._tick_spinner)

    def _tick_spinner(self) -> None:
        self._spinner_index = (self._spinner_index + 1) % len(self._spinner_frames)
        if self._spinner_index == 0:
            self._thinking_msg = random.choice(THINKING_MESSAGES)
        frame = self._spinner_frames[self._spinner_index]
        self.query_one("#spinner", Static).update(
            f"  [dim]{frame} {self._thinking_msg}...[/dim]"
        )

    def _stop_spinner(self) -> None:
        if self._spinner_timer:
            self._spinner_timer.stop()
            self._spinner_timer = None
        self.query_one("#spinner", Static).display = False

    def send_message(self, text: str) -> None:
        chat = self.query_one("#chat", RichLog)
        msg = Text()
        msg.append("You → ", style="bold #a6e3a1")
        msg.append(text)
        chat.write(msg)
        self._start_spinner()
        self.run_worker(self._get_response(text), exclusive=False, thread=True)

    def _get_response(self, text: str) -> None:
        """Run in thread to avoid blocking."""
        import subprocess
        cmd = build_command(text)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            raw = (result.stdout + result.stderr).strip()
            lines = [l for l in raw.splitlines() if l.strip().lower() not in ("completed", "sent", "queued")]
            response = "\n".join(lines).strip()
            self.call_from_thread(self._show_response, response)
        except Exception as e:
            self.call_from_thread(self._show_response, "", str(e))

    def _show_response(self, response: str, error: str = "") -> None:
        chat = self.query_one("#chat", RichLog)
        self._stop_spinner()
        if error:
            msg = Text()
            msg.append("Error: ", style="bold red")
            msg.append(error)
            chat.write(msg)
        elif response:
            msg = Text()
            msg.append(f"{DISPLAY_NAME} → ", style=f"bold {ACCENT}")
            msg.append(response)
            chat.write(msg)
        else:
            chat.write(Text("(no response)", style="dim"))
        chat.write(Text(""))  # blank line spacer


if __name__ == "__main__":
    ChatApp().run()
