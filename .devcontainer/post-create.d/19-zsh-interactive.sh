#!/usr/bin/env bash
# Source the tracked interactive zsh setup (aliases, zoxide, fzf, starship) from ~/.zshrc.
set -euo pipefail

POST_CREATE_D_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RC="$(cd "${POST_CREATE_D_DIR}/.." && pwd)/zsh/interactive.zsh"
ZSHRC="${HOME}/.zshrc"
BEGIN="# BEGIN project-template interactive"
END="# END project-template interactive"

if [[ ! -f "${RC}" ]]; then
	echo "Warning: ${RC} is missing; zsh keeps the image defaults." >&2
	exit 0
fi

block="$(
	printf '%s\n' "${BEGIN}"
	printf '[[ -r %q ]] && source %q\n' "${RC}" "${RC}"
	printf '%s\n' "${END}"
)"

# Drop any earlier block, then append so it runs after oh-my-zsh.
if [[ -f "${ZSHRC}" ]]; then
	tmp="$(mktemp)"
	awk -v begin="${BEGIN}" -v end="${END}" '
		$0 == begin { skip = 1; next }
		$0 == end { skip = 0; next }
		skip { next }
		/^$/ { blank++; next }
		{ while (blank > 0) { print ""; blank-- } print }
	' "${ZSHRC}" >"${tmp}"
	mv "${tmp}" "${ZSHRC}"
fi
printf '\n%s\n' "${block}" >>"${ZSHRC}"

echo "~/.zshrc sources ${RC}"
