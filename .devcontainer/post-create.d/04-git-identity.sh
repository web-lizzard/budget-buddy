#!/usr/bin/env bash
# Apply the host Git identity (HOST_GIT_USER_* from git.env) to this container.
set -euo pipefail

name="${HOST_GIT_USER_NAME:-}"
email="${HOST_GIT_USER_EMAIL:-}"

if [[ -z "${name}" && -z "${email}" ]]; then
	echo "Warning: host Git identity was not provided. Set user.name and user.email on the host, then rebuild." >&2
	exit 0
fi

if [[ -n "${name}" ]]; then
	git config --global user.name "${name}"
	echo "git user.name: ${name}"
else
	echo "Warning: HOST_GIT_USER_NAME is empty; user.name was not set." >&2
fi

if [[ -n "${email}" ]]; then
	git config --global user.email "${email}"
	echo "git user.email: ${email}"
else
	echo "Warning: HOST_GIT_USER_EMAIL is empty; user.email was not set." >&2
fi
