#!/usr/bin/env bash
# Point every zsh at the workspace .env (interactive, login, and scripts).
set -euo pipefail

POST_CREATE_D_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "${POST_CREATE_D_DIR}/../.." && pwd)"
EXPORTER="${WORKSPACE_ROOT}/.devcontainer/zsh/export-dotenv.zsh"
ENV_FILE="${WORKSPACE_ROOT}/.env"
ZSHENV="${HOME}/.zshenv"
BEGIN="# BEGIN project-template dotenv"
END="# END project-template dotenv"

if [[ ! -f "${EXPORTER}" ]]; then
	echo "Warning: ${EXPORTER} is missing; zsh will not export .env." >&2
	exit 0
fi

block="$(
	printf '%s\n' "${BEGIN}"
	printf '[[ -r %q ]] && source %q %q\n' "${EXPORTER}" "${EXPORTER}" "${ENV_FILE}"
	printf '%s\n' "${END}"
)"

if [[ -f "${ZSHENV}" ]] && grep -qF "${BEGIN}" "${ZSHENV}"; then
	tmp="$(mktemp)"
	awk -v begin="${BEGIN}" -v end="${END}" '
		$0 == begin { skip = 1; next }
		$0 == end { skip = 0; next }
		skip { next }
		{ print }
	' "${ZSHENV}" >"${tmp}"
	if [[ -s "${tmp}" ]]; then
		printf '\n%s\n' "${block}" >>"${tmp}"
		mv "${tmp}" "${ZSHENV}"
	else
		printf '%s\n' "${block}" >"${ZSHENV}"
		rm -f "${tmp}"
	fi
else
	if [[ -f "${ZSHENV}" && -s "${ZSHENV}" ]]; then
		printf '\n%s\n' "${block}" >>"${ZSHENV}"
	else
		printf '%s\n' "${block}" >"${ZSHENV}"
	fi
fi

echo "zsh will export ${ENV_FILE} from ${ZSHENV}"
