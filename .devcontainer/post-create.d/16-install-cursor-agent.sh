#!/usr/bin/env bash
# Installs the Cursor Agent CLI (`agent`). Login lives on the shared
# `cursor-agent` volume at ~/.config/cursor, which holds auth.json only.
set -euo pipefail

CURSOR_DIR="${HOME}/.config/cursor"

# Docker creates a named volume as root:root when the image has no directory to copy from.
if [[ -d "${CURSOR_DIR}" && ! -w "${CURSOR_DIR}" ]]; then
	sudo chown -R "$(id -u):$(id -g)" "${CURSOR_DIR}"
fi

if command -v agent >/dev/null 2>&1; then
	echo "Cursor Agent CLI already installed: $(agent --version 2>/dev/null || echo 'version unknown')"
else
	echo "Installing Cursor Agent CLI ..."
	curl https://cursor.com/install -fsS | bash

	if ! command -v agent >/dev/null 2>&1; then
		echo "Cursor Agent CLI install finished but 'agent' is not on PATH." >&2
		echo "Ensure ~/.local/bin is in PATH, then open a new shell." >&2
		exit 1
	fi

	echo "Cursor Agent CLI installed: $(agent --version)"
fi

if agent status --format json | grep -q '"isAuthenticated"[[:space:]]*:[[:space:]]*true'; then
	echo "agent status reports isAuthenticated: true."
else
	echo "agent status does not report isAuthenticated: true."
	echo "Run 'agent login' once (with NO_OPEN_BROWSER=1 when the browser does not open)."
fi
