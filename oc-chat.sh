#!/bin/bash
# oc-chat.sh — Talk to any OpenClaw agent from your terminal
#
# Supports both local and remote (SSH) OpenClaw instances.
# Messages are prefixed with [terminal] so agents can detect
# the medium and adjust formatting (no markdown in terminals).
#
# Usage: ./oc-chat.sh [options]
#   -a, --agent NAME      Agent name (default: main)
#   -s, --server HOST     SSH host for remote OpenClaw (default: localhost)
#   -c, --color HEX       Hex color for agent responses (default: d97757)
#   -n, --name LABEL      Display name for the agent (default: agent name)
#   --no-tag              Don't prepend [terminal] to messages
#   -h, --help            Show this help
#
# Examples:
#   ./oc-chat.sh                              # local main agent
#   ./oc-chat.sh -a tutor -s myserver         # remote tutor agent
#   ./oc-chat.sh -a main -s north -c d97757   # remote, custom color
#   ./oc-chat.sh -a main -n claude            # custom display name
#
# Environment:
#   OPENCLAW    Path to openclaw binary (default: openclaw)
#               Set this if openclaw isn't in your PATH, e.g.:
#               export OPENCLAW=/home/user/.nvm/versions/node/v22/bin/openclaw

set -euo pipefail

# Defaults
AGENT="main"
SERVER="localhost"
COLOR_HEX="d97757"
DISPLAY_NAME=""
TAG_MESSAGES=true

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    -a|--agent) AGENT="$2"; shift 2 ;;
    -s|--server) SERVER="$2"; shift 2 ;;
    -c|--color) COLOR_HEX="$2"; shift 2 ;;
    -n|--name) DISPLAY_NAME="$2"; shift 2 ;;
    --no-tag) TAG_MESSAGES=false; shift ;;
    -h|--help)
      echo "Usage: oc-chat.sh [options]"
      echo ""
      echo "Talk to any OpenClaw agent from your terminal."
      echo ""
      echo "Options:"
      echo "  -a, --agent NAME      Agent name (default: main)"
      echo "  -s, --server HOST     SSH host for remote OpenClaw (default: localhost)"
      echo "  -c, --color HEX       Hex color for agent responses (default: d97757)"
      echo "  -n, --name LABEL      Display name for the agent (default: agent name)"
      echo "  --no-tag              Don't prepend [terminal] to messages"
      echo "  -h, --help            Show this help"
      echo ""
      echo "Examples:"
      echo "  oc-chat.sh                                # local main agent"
      echo "  oc-chat.sh -a tutor -s myserver           # remote tutor via SSH"
      echo "  oc-chat.sh -a main -s north -c 36b5a0     # custom color"
      echo "  oc-chat.sh -a main -n claude              # custom display name"
      echo ""
      echo "Environment:"
      echo "  OPENCLAW    Path to openclaw binary (default: openclaw)"
      echo "              For remote servers where openclaw is installed via nvm,"
      echo "              set this to the full path so SSH can find it."
      echo ""
      echo "How it works:"
      echo "  Local mode (default):  runs openclaw directly on this machine"
      echo "  Remote mode (-s host): runs openclaw on the remote host via SSH"
      echo "  Messages get a [terminal] prefix so agents can skip markdown."
      exit 0
      ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

LABEL="${DISPLAY_NAME:-$AGENT}"

# OpenClaw binary and remote PATH setup
OPENCLAW="${OPENCLAW:-openclaw}"
OPENCLAW_DIR=$(dirname "$OPENCLAW")
if [[ "$OPENCLAW_DIR" != "." ]]; then
  REMOTE_PATH="PATH=$OPENCLAW_DIR:\$PATH"
else
  REMOTE_PATH=""
fi

# Parse hex color to RGB for true color (24-bit) escape
R=$((16#${COLOR_HEX:0:2}))
G=$((16#${COLOR_HEX:2:2}))
B=$((16#${COLOR_HEX:4:2}))

BOLD="\033[1m"
AGENT_COLOR="\033[38;2;${R};${G};${B}m"
GREEN="\033[32m"
DIM="\033[2m"
RESET="\033[0m"

# Header
echo -e "${AGENT_COLOR}${BOLD}${LABEL}${RESET} ${DIM}— terminal${RESET}"
echo -e "${DIM}Type your message and press Enter. Ctrl+C to exit.${RESET}"
echo ""

# Escape single quotes for shell
escape_msg() {
  echo "$1" | sed "s/'/'\\\\''/g"
}

# Send message to agent
send_message() {
  local msg="$1"

  if [[ "$TAG_MESSAGES" == true ]]; then
    msg="[terminal] $msg"
  fi

  local escaped
  escaped=$(escape_msg "$msg")

  if [[ "$SERVER" == "localhost" ]]; then
    $OPENCLAW agent --agent "$AGENT" --message "$escaped" 2>&1
  else
    if [[ -n "$REMOTE_PATH" ]]; then
      ssh "$SERVER" "$REMOTE_PATH $OPENCLAW agent --agent $AGENT --message '$escaped'" 2>&1
    else
      ssh "$SERVER" "$OPENCLAW agent --agent $AGENT --message '$escaped'" 2>&1
    fi
  fi
}

# Main loop
while true; do
  echo -ne "${GREEN}you → ${RESET}"
  read -r msg || break  # handle EOF (Ctrl+D)
  if [ -z "$msg" ]; then continue; fi
  if [[ "$msg" == "quit" || "$msg" == "exit" || "$msg" == "bye" ]]; then
    echo -e "${DIM}See you later.${RESET}"
    break
  fi

  echo ""
  response=$(send_message "$msg")
  if [ -n "$response" ]; then
    echo -e "${AGENT_COLOR}${LABEL} →${RESET} $(echo "$response" | head -1)"
    echo "$response" | tail -n +2 | sed "s/^/    /"
  else
    echo -e "${DIM}(no response — check connection)${RESET}"
  fi
  echo ""
done
