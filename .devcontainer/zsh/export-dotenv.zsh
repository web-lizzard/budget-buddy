# Sourced from ~/.zshenv. Exports KEY=VALUE lines from the .env path in $1.
# Literals only — values are not evaluated.
() {
	emulate -L zsh

	local env_file="${1:-}"
	[[ -n ${env_file} && -f ${env_file} && -r ${env_file} ]] || return 0

	local line key val
	while IFS= read -r line || [[ -n ${line} ]]; do
		line=${line%$'\r'}
		[[ -z ${line} || ${line} == \#* ]] && continue
		if [[ ${line} == 'export '* ]]; then
			line=${line#export }
		fi
		[[ ${line} == *=* ]] || continue
		key=${line%%=*}
		[[ ${key} =~ '^[A-Za-z_][A-Za-z0-9_]*$' ]] || continue
		val=${line#*=}
		if [[ ${val} == \"*\" && ${val} == *\" ]]; then
			val=${val#\"}
			val=${val%\"}
		elif [[ ${val} == \'*\' && ${val} == *\' ]]; then
			val=${val#\'}
			val=${val%\'}
		fi
		export "${key}=${val}"
	done <"${env_file}"

	# ordo reads GITHUB_TOKEN; install uses GITHUB_PACKAGES_TOKEN. One classic PAT covers both.
	if [[ -z ${GITHUB_TOKEN:-} && -n ${GITHUB_PACKAGES_TOKEN:-} ]]; then
		export GITHUB_TOKEN="${GITHUB_PACKAGES_TOKEN}"
	fi
} "$@"
