#!/usr/bin/env bash
# Host-only: refresh the vendored Omarchy defaults from the Omarchy installed on this machine.
# They are the fallback configs used in the container when the matching host config is
# missing or empty (see the README, "Defaults when a host config is missing").
# Run it after an Omarchy update, review the diff, and commit.
set -euo pipefail

DEST="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OMARCHY=/usr/share/omarchy
OMARCHY_NVIM=/usr/share/omarchy-nvim/config

for src in "${OMARCHY}/config/tmux/tmux.conf" "${OMARCHY}/config/lazygit/config.yml" \
	"${OMARCHY}/config/starship.toml" "${OMARCHY_NVIM}/init.lua"; do
	if [[ ! -e "${src}" ]]; then
		echo "Missing ${src}; is this an Omarchy host with omarchy-nvim installed?" >&2
		exit 1
	fi
done

cp "${OMARCHY}/config/tmux/tmux.conf" "${DEST}/tmux.conf"
cp "${OMARCHY}/config/lazygit/config.yml" "${DEST}/lazygit.yml"
cp "${OMARCHY}/config/starship.toml" "${DEST}/starship.toml"

rm -rf "${DEST}/nvim"
cp -r "${OMARCHY_NVIM}" "${DEST}/nvim"

# On Omarchy, lua/plugins/theme.lua is a symlink to the current theme's neovim.lua and is
# not shipped by omarchy-nvim. Load it from the mounted theme directory instead.
cat >"${DEST}/nvim/lua/plugins/theme.lua" <<'LUA'
-- Not part of omarchy-nvim: on Omarchy this file is a symlink to the current theme's
-- neovim.lua. Load it from the mounted theme directory when the host has one; otherwise
-- LazyVim keeps its default colorscheme.
local theme = vim.fn.expand("~/.local/state/omarchy/current/theme/neovim.lua")
if vim.uv.fs_stat(theme) then
	return dofile(theme)
end
return {}
LUA

{
	echo "omarchy $(cat "${OMARCHY}/version")"
	pacman -Q omarchy-nvim
} >"${DEST}/VERSION"

echo "Vendored Omarchy defaults refreshed in ${DEST}:"
cat "${DEST}/VERSION"
