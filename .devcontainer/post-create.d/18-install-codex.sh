#!/usr/bin/env bash
# Installs the Codex CLI (`codex`). Login lives on the `codex` volume at
# ~/.codex, which holds auth.json.
set -euo pipefail

CODEX_DIR="${HOME}/.codex"

# Docker creates a named volume as root:root when the image has no directory to copy from.
if [[ -d "${CODEX_DIR}" && ! -w "${CODEX_DIR}" ]]; then
	sudo chown -R "$(id -u):$(id -g)" "${CODEX_DIR}"
fi

if command -v codex >/dev/null 2>&1; then
	echo "Codex CLI already installed: $(codex --version 2>/dev/null || echo 'version unknown')"
else
	echo "Installing Codex CLI ..."
	npm install -g @openai/codex

	if ! command -v codex >/dev/null 2>&1; then
		echo "Codex CLI install finished but 'codex' is not on PATH." >&2
		echo "Ensure the global npm prefix bin directory is in PATH, then open a new shell." >&2
		exit 1
	fi

	echo "Codex CLI installed: $(codex --version)"
fi

if [[ -f "${CODEX_DIR}/auth.json" ]]; then
	echo "Codex login found at ${CODEX_DIR}/auth.json."
else
	echo "No Codex login found at ${CODEX_DIR}/auth.json."
	echo "Run 'codex login --device-auth' once."
fi
