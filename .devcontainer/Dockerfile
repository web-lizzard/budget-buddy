FROM mcr.microsoft.com/devcontainers/base:ubuntu

# The base image ships a `vscode` user (uid 1000). Rename it to an editor-neutral `dev`,
# keeping the uid/gid, home contents (oh-my-zsh) and passwordless sudo.
RUN usermod -l dev -d /home/dev -m vscode \
	&& groupmod -n dev vscode \
	&& echo 'dev ALL=(root) NOPASSWD:ALL' >/etc/sudoers.d/dev \
	&& chmod 440 /etc/sudoers.d/dev \
	&& rm /etc/sudoers.d/vscode

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
	&& apt-get install -y --no-install-recommends zsh tmux ripgrep fd-find fzf bat zoxide \
	&& ln -sf /usr/bin/fdfind /usr/local/bin/fd \
	&& ln -sf /usr/bin/batcat /usr/local/bin/bat \
	&& rm -rf /var/lib/apt/lists/*

# lazygit is not in the Ubuntu repos. Pinned release, verified against the release checksums.
ARG LAZYGIT_VERSION=0.65.0
RUN set -eu; \
	case "$(dpkg --print-architecture)" in \
		amd64) arch=x86_64 ;; \
		arm64) arch=arm64 ;; \
		*) echo "Unsupported architecture for lazygit: $(dpkg --print-architecture)" >&2; exit 1 ;; \
	esac; \
	file="lazygit_${LAZYGIT_VERSION}_linux_${arch}.tar.gz"; \
	url="https://github.com/jesseduffield/lazygit/releases/download/v${LAZYGIT_VERSION}"; \
	cd /tmp; \
	curl -fsSLO "${url}/${file}"; \
	curl -fsSL "${url}/checksums.txt" | grep " ${file}\$" | sha256sum -c -; \
	tar -xzf "${file}" -C /usr/local/bin lazygit; \
	rm -f "${file}"

# Ubuntu's neovim is too old for LazyVim (needs >= 0.11). Pinned release, verified against the
# per-asset sha256 digests published by GitHub for that release.
ARG NEOVIM_VERSION=0.12.5
ARG NEOVIM_SHA256_X86_64=bce0f56eda1f1b1db6eee8f4133d7a38813ea07933837dd1777411ca384c6875
ARG NEOVIM_SHA256_ARM64=1aa5ca085249580ae0f91eb14f27ec0919773ff2d99a163d03f3d6c21ac29725
RUN set -eu; \
	case "$(dpkg --print-architecture)" in \
		amd64) arch=x86_64; sha="${NEOVIM_SHA256_X86_64}" ;; \
		arm64) arch=arm64; sha="${NEOVIM_SHA256_ARM64}" ;; \
		*) echo "Unsupported architecture for neovim: $(dpkg --print-architecture)" >&2; exit 1 ;; \
	esac; \
	file="nvim-linux-${arch}.tar.gz"; \
	cd /tmp; \
	curl -fsSLO "https://github.com/neovim/neovim/releases/download/v${NEOVIM_VERSION}/${file}"; \
	echo "${sha}  ${file}" | sha256sum -c -; \
	tar -xzf "${file}" -C /opt; \
	ln -sf "/opt/nvim-linux-${arch}/bin/nvim" /usr/local/bin/nvim; \
	rm -f "${file}"

# eza and starship are not in the Ubuntu repos (zsh/interactive.zsh uses them for `ls` and the
# prompt). Pinned releases, verified against the per-asset sha256 digests GitHub publishes.
ARG EZA_VERSION=0.23.5
ARG EZA_SHA256_X86_64=35c70c5c43c29108075e58b893234c67ef585f0b53a7eaf8e9e7d4eec9f339b4
ARG EZA_SHA256_ARM64=40b87ae8628aa2ff0f0d2dc24ab52f689631366385c3da630bae745671fd71ec
ARG STARSHIP_VERSION=1.26.0
ARG STARSHIP_SHA256_X86_64=b7c232b0e8249d8e55a40beb79c5c43a7d370f3f9408bd215deb0170daeaadf3
ARG STARSHIP_SHA256_ARM64=dc30189378d2f2e287384e8a692d3f95ad1df64cf0e8c36aa9201516028aed6b
RUN set -eu; \
	case "$(dpkg --print-architecture)" in \
		amd64) arch=x86_64; eza_sha="${EZA_SHA256_X86_64}"; starship_sha="${STARSHIP_SHA256_X86_64}" ;; \
		arm64) arch=aarch64; eza_sha="${EZA_SHA256_ARM64}"; starship_sha="${STARSHIP_SHA256_ARM64}" ;; \
		*) echo "Unsupported architecture for eza/starship: $(dpkg --print-architecture)" >&2; exit 1 ;; \
	esac; \
	cd /tmp; \
	eza_file="eza_${arch}-unknown-linux-gnu.tar.gz"; \
	curl -fsSLO "https://github.com/eza-community/eza/releases/download/v${EZA_VERSION}/${eza_file}"; \
	echo "${eza_sha}  ${eza_file}" | sha256sum -c -; \
	tar -xzf "${eza_file}" -C /usr/local/bin ./eza; \
	starship_file="starship-${arch}-unknown-linux-musl.tar.gz"; \
	curl -fsSLO "https://github.com/starship/starship/releases/download/v${STARSHIP_VERSION}/${starship_file}"; \
	echo "${starship_sha}  ${starship_file}" | sha256sum -c -; \
	tar -xzf "${starship_file}" -C /usr/local/bin starship; \
	rm -f "${eza_file}" "${starship_file}"

# tmux config: new windows and panes start in the current pane's directory.
# The host's ~/.config/tmux is mounted on top (see devcontainer.json) and is read after this file;
# when it is empty, /etc/tmux.conf sources the vendored Omarchy defaults instead.
COPY tmux.conf /etc/tmux.conf
COPY omarchy/tmux.conf /etc/tmux/omarchy.conf

# Default login shell for the devcontainer user (Cursor integrated terminal picks this up too).
RUN chsh -s /usr/bin/zsh dev

# User-local CLIs (ordo, Claude Code) without breaking the image PATH in containerEnv.
ENV PATH="/home/dev/.local/bin:${PATH}"

# A fresh named volume copies ownership from this directory. Without it Docker
# creates the mount as root and Claude Code cannot write credentials.
RUN mkdir -p /home/dev/.claude && chown -R dev:dev /home/dev/.claude

# Same for the Agent CLI login and the nvim-data volume. Volume targets must exist and be
# dev-owned, or a fresh volume is root-owned (cursor-agent cannot save credentials,
# lazy.nvim cannot install plugins). ~/.local/state is created too: otherwise Docker
# creates it as root for the Omarchy theme bind mount and Claude Code, nvim and zoxide
# cannot write state there.
RUN mkdir -p /home/dev/.config/cursor /home/dev/.local/share/nvim /home/dev/.local/state \
	&& chown -R dev:dev /home/dev/.config /home/dev/.local \
	&& chmod 700 /home/dev/.config/cursor

# Same for the Codex CLI login. A fresh codex volume copies ownership from this
# directory, so it must exist and be dev-owned for auth.json to be written.
RUN mkdir -p /home/dev/.codex \
	&& chown dev:dev /home/dev/.codex \
	&& chmod 700 /home/dev/.codex
