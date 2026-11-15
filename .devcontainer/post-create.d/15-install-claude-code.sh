#!/usr/bin/env bash
# Installs Claude Code CLI. Login lives on the shared `claude-code` volume
# (CLAUDE_CONFIG_DIR), not in CLAUDE_CODE_OAUTH_TOKEN — that token cannot start Remote Control.
set -euo pipefail

CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-${HOME}/.claude}"

if [[ -n "${CLAUDE_CODE_OAUTH_TOKEN:-}" ]]; then
	echo "Warning: CLAUDE_CODE_OAUTH_TOKEN is set. It overrides /login and cannot start Remote Control. Unset it." >&2
fi

# Docker creates a named volume as root:root when the image has no directory to copy from.
if [[ -d "${CLAUDE_DIR}" && ! -w "${CLAUDE_DIR}" ]]; then
	sudo chown -R "$(id -u):$(id -g)" "${CLAUDE_DIR}"
fi

if command -v claude >/dev/null 2>&1; then
	echo "Claude Code already installed: $(claude --version 2>/dev/null || echo 'version unknown')"
else
	echo "Installing Claude Code ..."
	curl -fsSL https://claude.ai/install.sh | bash

	if ! command -v claude >/dev/null 2>&1; then
		echo "Claude Code install finished but 'claude' is not on PATH." >&2
		echo "Ensure ~/.local/bin is in PATH, then open a new shell." >&2
		exit 1
	fi

	echo "Claude Code installed: $(claude --version)"
fi

if [[ -f "${CLAUDE_DIR}/.credentials.json" ]]; then
	echo "Claude Code login found on the shared volume (${CLAUDE_DIR})"
else
	echo "No Claude Code login on the shared volume yet."
	echo "Run 'claude' once in any project from this template and complete /login."
	echo "That session is reused by every other container mounting the claude-code volume."
fi
