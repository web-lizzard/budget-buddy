#!/usr/bin/env bash
# devcontainer.json bind-mounts the host's ~/.config/nvim. When that directory is empty
# (host has no Neovim config), link the vendored Omarchy config under .devcontainer/omarchy/nvim
# as ~/.config/nvim-omarchy; zsh/interactive.zsh then sets NVIM_APPNAME=nvim-omarchy.
# Nothing is written into the host's config. Without the mount, ~/.config/nvim itself
# is linked to the vendored config.
# Refresh it from the host's Omarchy with omarchy/sync.sh.
set -euo pipefail

REPO_NVIM="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/omarchy/nvim"
TARGET="${HOME}/.config/nvim"

if [[ ! -d "${REPO_NVIM}" ]]; then
	echo "No vendored nvim config at ${REPO_NVIM}; skipping."
	exit 0
fi

FALLBACK="${HOME}/.config/nvim-omarchy"

# Never replace a real directory: with the host mount in place, removing it would
# delete the host config.
if [[ -d "${TARGET}" && ! -L "${TARGET}" ]]; then
	if [[ -n "$(ls -A "${TARGET}")" ]]; then
		echo "Using host Neovim config at ${TARGET}."
		exit 0
	fi
	ln -sfn "${REPO_NVIM}" "${FALLBACK}"
	echo "${TARGET} is empty; linked ${FALLBACK} -> ${REPO_NVIM} (NVIM_APPNAME=nvim-omarchy)."
	exit 0
fi

mkdir -p "${HOME}/.config"

if [[ -L "${TARGET}" ]]; then
	current="$(readlink "${TARGET}")"
	if [[ "${current}" == "${REPO_NVIM}" ]]; then
		echo "Neovim config already linked to ${REPO_NVIM}"
		exit 0
	fi
	rm "${TARGET}"
fi

ln -s "${REPO_NVIM}" "${TARGET}"
echo "Linked ${TARGET} -> ${REPO_NVIM}"
