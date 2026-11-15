#!/usr/bin/env bash
# Host-only: make sure the bind-mount sources in devcontainer.json exist.
# Docker refuses to create the container when a bind source is missing.
set -euo pipefail

# Host tool configs. Missing ones are created empty, so the container falls back to the
# vendored Omarchy defaults in .devcontainer/omarchy/ instead of failing to start.
# Existing files are never touched.
#   ~/.config/tmux                       read-only; empty -> omarchy/tmux.conf (/etc/tmux.conf)
#   ~/.config/nvim                       read-only; empty -> omarchy/nvim (17-link-nvim-config.sh)
#   ~/.local/state/omarchy/current/theme read-only; Omarchy theme, read by both nvim configs
#   ~/.config/lazygit                    read-only; config.yml must exist, or lazygit tries
#                                        to create it and fails on the read-only mount;
#                                        empty -> omarchy/lazygit.yml (zsh/interactive.zsh)
#   ~/.config/starship.toml              read-only; empty -> omarchy/starship.toml (zsh/interactive.zsh)
mkdir -p \
	"${HOME}/.config/tmux" \
	"${HOME}/.config/nvim" \
	"${HOME}/.local/state/omarchy/current/theme" \
	"${HOME}/.config/lazygit"
[[ -e "${HOME}/.config/lazygit/config.yml" ]] || touch "${HOME}/.config/lazygit/config.yml"
[[ -e "${HOME}/.config/starship.toml" ]] || touch "${HOME}/.config/starship.toml"

# SSH agent from gcr (gnome-keyring). The directory is mounted rather than the
# socket itself, because the agent recreates the socket on every login.
if [[ -z "${XDG_RUNTIME_DIR:-}" ]]; then
	echo "XDG_RUNTIME_DIR is not set; the SSH agent mount needs a Linux host session." >&2
	exit 1
fi
mkdir -p "${XDG_RUNTIME_DIR}/gcr"

if [[ ! -S "${XDG_RUNTIME_DIR}/gcr/ssh" ]]; then
	echo "Warning: no SSH agent socket at ${XDG_RUNTIME_DIR}/gcr/ssh." >&2
	echo "Run 'systemctl --user enable --now gcr-ssh-agent.socket' for git over SSH in the container." >&2
fi
