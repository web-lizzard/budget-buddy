# Interactive zsh setup modeled on Omarchy's bash defaults (/usr/share/omarchy/default/bash).
# Sourced at the end of ~/.zshrc (after oh-my-zsh), so these aliases and the prompt win.

# Editor and pagers
export EDITOR=nvim
# Host configs that are missing (empty mounts) fall back to the vendored Omarchy defaults in
# .devcontainer/omarchy/; see 07-ensure-host-mounts.sh.
() {
	local omarchy=${${(%):-%x}:A:h:h}/omarchy
	local nvim_files=("${HOME}"/.config/nvim/*(DN[1]))
	# Neovim: the vendored config is linked as ~/.config/nvim-omarchy by 17-link-nvim-config.sh.
	if [[ -d ${HOME}/.config/nvim-omarchy ]] && (( ${#nvim_files} == 0 )); then
		export NVIM_APPNAME=nvim-omarchy
	fi
	[[ -s ${HOME}/.config/lazygit/config.yml ]] || export LG_CONFIG_FILE=${omarchy}/lazygit.yml
	[[ -s ${HOME}/.config/starship.toml ]] || export STARSHIP_CONFIG=${omarchy}/starship.toml
}
export SUDO_EDITOR="${EDITOR}"
export BAT_THEME=ansi
if (( $+commands[bat] && $+commands[col] )); then
	export MANROFFOPT="-c"
	export MANPAGER="sh -c 'col -bx | bat -l man -p'"
fi

# History: large, shared across panes, and never record commands carrying tokens.
HISTSIZE=32768
SAVEHIST=${HISTSIZE}
setopt APPEND_HISTORY SHARE_HISTORY HIST_IGNORE_SPACE HIST_IGNORE_DUPS
zshaddhistory() {
	[[ $1 != *(sk-ant-|ghp_|github_pat_|CLAUDE_CODE_OAUTH_TOKEN=)* ]]
}

# File system
if (( $+commands[eza] )); then
	alias ls='eza -lh --group-directories-first --icons=auto'
	alias lsa='ls -a'
	alias lt='eza --tree --level=2 --long --icons --git'
	alias lta='lt -a'
fi

if (( $+commands[fzf] )); then
	alias ff="fzf --preview 'bat --style=numbers --color=always {}'"
	alias eff='${EDITOR} "$(ff)"'
	# fzf >= 0.48 ships its own zsh integration; Debian's older fzf keeps it under examples/.
	if fzf --zsh >/dev/null 2>&1; then
		source <(fzf --zsh)
	else
		for f in /usr/share/doc/fzf/examples/{key-bindings,completion}.zsh; do
			[[ -r ${f} ]] && source "${f}"
		done
	fi
fi

if (( $+commands[zoxide] )); then
	eval "$(zoxide init zsh)"
	alias cd='zd'
	zd() {
		if (( $# == 0 )); then
			builtin cd ~ || return
		elif [[ -d $1 ]]; then
			builtin cd "$1" || return
		else
			if ! z "$@"; then
				echo "Error: Directory not found"
				return 1
			fi
			printf "\U000F17A9 "
			pwd
		fi
	}
fi

# Directories
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'

# Tools
alias cx='printf "\033[2J\033[3J\033[H" && claude --permission-mode auto'
alias t='tmux attach || tmux new -s Work'
n() { if (( $# == 0 )); then command nvim .; else command nvim "$@"; fi }

# Git (override oh-my-zsh's git plugin, where gcm means checkout main)
alias g='git'
alias gcm='git commit -m'
alias gcam='git commit -a -m'
alias gcad='git commit -a --amend'

# Prompt: starship reads the host's ~/.config/starship.toml (bind-mounted read-only),
# or the vendored Omarchy one when that file is empty.
if (( $+commands[starship] )) && [[ ${TERM:-} != dumb ]]; then
	eval "$(starship init zsh)"
fi
