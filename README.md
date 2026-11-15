# project-template

## Dev container: Ordo (skills)

On **Rebuild Container**, `postCreateCommand` runs `.devcontainer/post-create.sh`, which executes every `*.sh` script in `post-create.d/` in sorted order. Step **`08-install-ordo.sh`** installs [`@web-lizzard/ordo`](https://github.com/web-lizzard/ordo) globally so `ordo` is available in the integrated terminal.

### Setup

1. Copy `.env.example` to `.env` and set `GITHUB_PACKAGES_TOKEN` to a **classic** GitHub PAT with the `read:packages` and `repo` scopes.
2. Rebuild the dev container. On the host, `initialize.d/05-sync-devcontainer-env.sh` copies the token into `.devcontainer/devcontainer.env`, which Docker injects via `runArgs` (`localEnv` in `devcontainer.json` does **not** read `.env` on its own). Step **`07-export-dotenv.sh`** adds a block to `~/.zshenv` so every zsh sources `.env` through `.devcontainer/zsh/export-dotenv.zsh`. When `GITHUB_TOKEN` is unset, that value is also exported as `GITHUB_TOKEN` for `ordo`.
3. Inside the container, verify: `ordo status`

Edit `.env` on the host and open a new terminal to pick up changes. A rebuild is only required the first time, so the `~/.zshenv` hook exists.

### Managing skills

Ordo pulls skills and related artifacts from the internal GitHub repository:

```sh
ordo add <capability>       # install capability artifacts (e.g. skills)
ordo status                 # list installed capabilities and versions
ordo update                 # update within installed major versions
ordo remove <capability>    # remove a capability
```

Installed skills land under `.cursor/skills/` (gitignored).

## Dev container: Git identity

On container create, `initialize.d/06-sync-git-identity.sh` reads the host identity Git would use for this repo (`user.name` and `user.email`, including a local override) and writes `.devcontainer/git.env`. Docker injects that file via `runArgs`. `post-create.d/04-git-identity.sh` copies the values into the container's global Git config.

`git.env` is generated and gitignored. Change the name or email on the host, then rebuild the container to pick it up. Credential helpers and the rest of `~/.gitconfig` stay on the host.

## Dev container: Claude Code

Authentication is a normal `/login` stored on one Docker named volume, `claude-code`, mounted at `/home/dev/.claude`. `CLAUDE_CONFIG_DIR` points at that same path, so `.credentials.json` and `.claude.json` stay on the volume. A `CLAUDE_CODE_OAUTH_TOKEN` from `claude setup-token` is not used: it can call the model, but it cannot start Remote Control, and it overrides the subscription login.

The volume name is fixed (no `${devcontainerId}`). Every project built from this template, on the same Docker host, mounts the same volume. Log in once inside any of those containers; the others see the same session, including ones created later. Rebuilds do not drop the login.

On first launch, if the browser cannot reach the callback inside the container, press `c` in `claude`, open the URL on the host, and paste the code back into the terminal.

## Dev container: post-create setup

On **Rebuild Container**, `postCreateCommand` also runs:

- **`04-git-identity.sh`** — copies the host `user.name` and `user.email` into the container Git config.
- **`07-export-dotenv.sh`** — sources workspace `.env` from `~/.zshenv` for every zsh.
- **`10-pre-commit.sh`** — installs [pre-commit](https://pre-commit.com/) and registers git hooks. The repo config (`.pre-commit-config.yaml`) starts with trailing-whitespace only; extend hooks as the project grows.
- **`11-github-known-hosts.sh`** — pins GitHub's SSH host keys, so the first `git pull`/`push` over SSH does not stop at a prompt.
- **`15-install-claude-code.sh`** — installs Claude Code CLI. Login is read from the shared `claude-code` volume.
- **`16-install-cursor-agent.sh`** — installs the Cursor Agent CLI (`agent`). Run `agent login` once per `cursor-agent` volume (with `NO_OPEN_BROWSER=1` when the browser does not open).
- **`17-link-nvim-config.sh`** — links the vendored Omarchy Neovim config when the host has no Neovim config (see below).
- **`18-install-codex.sh`** — installs the Codex CLI. Run `codex login --device-auth` once per `codex` volume.
- **`19-zsh-interactive.sh`** — sources `.devcontainer/zsh/interactive.zsh` at the end of `~/.zshrc`.

Add new in-container setup steps as numbered scripts in `.devcontainer/post-create.d/`.

## Dev container: dev tools and host configs

The image provides pinned, checksum-verified `nvim`, `lazygit`, `eza` and `starship` (versions are `ARG`s in the Dockerfile), plus `tmux`, `ripgrep`, `fd`, `fzf`, `bat` and `zoxide` from apt. Cursor remains the default editor.

Host configs are mounted into the container **read-only**, so tools behave the same as on the host and nothing in the container can change them:

| Host path | Container | Mode |
|-----------|-----------|------|
| `~/.config/nvim` | `~/.config/nvim` | read-only |
| `~/.config/tmux` | `~/.config/tmux` | read-only, read after the image's `/etc/tmux.conf` |
| `~/.config/lazygit` | `~/.config/lazygit` | read-only |
| `~/.config/starship.toml` | `~/.config/starship.toml` | read-only |
| `~/.local/state/omarchy/current/theme` | same path | read-only; target of the Omarchy theme symlinks |
| `$XDG_RUNTIME_DIR/gcr` | `/run/host-ssh` | host SSH agent (`SSH_AUTH_SOCK`) |

Neovim plugins install at the versions pinned in the host's `lazy-lock.json`. lazy.nvim cannot write that file back, so the first install into an empty `nvim-data` volume ends with a `lazy-lock.json: Read-only file system` error (plugins are installed anyway; later starts are clean), and `:Lazy update` fails. Update plugins on the host; the container picks up the new lockfile on the next `:Lazy restore`.

Logins and plugin data live on named volumes shared by every project from this template: `claude-code`, `cursor-agent`, `codex`, and `nvim-data` (`~/.local/share/nvim`, plugins and Mason). They survive rebuilds.

### Defaults when a host config is missing

The host config always wins. When there is nothing to mount (a machine without these configs, e.g. a fresh box or a VPS), each tool falls back to **Omarchy's defaults**, vendored in `.devcontainer/omarchy/`. `initialize.d/07-ensure-host-mounts.sh` creates any absent mount source empty and never touches existing ones, so the container still starts; an empty mount is what switches a tool to its fallback:

- **Neovim** — when `~/.config/nvim` is empty, `post-create.d/17-link-nvim-config.sh` links `.devcontainer/omarchy/nvim/` (the `omarchy-nvim` LazyVim config) as `~/.config/nvim-omarchy`, and zsh sets `NVIM_APPNAME=nvim-omarchy`. Nothing is written into the host config. Its `lua/plugins/theme.lua` loads the mounted Omarchy theme when there is one, else LazyVim's default colorscheme. Plugin data lives in `~/.local/share/nvim-omarchy`, outside the `nvim-data` volume, and is re-downloaded after a rebuild.
- **tmux** — when `~/.config/tmux/tmux.conf` is missing or empty, `/etc/tmux.conf` sources `.devcontainer/omarchy/tmux.conf` (baked into the image as `/etc/tmux/omarchy.conf`). The template's own tweaks in `.devcontainer/tmux.conf` (panes and windows in the current directory, mouse on) apply either way. The `prefix ?` keybinding popup calls an Omarchy host command and does not work in the container.
- **lazygit** — an empty `config.yml` is created, since lazygit fails trying to create it on a read-only mount; while it is empty, zsh points `LG_CONFIG_FILE` at `.devcontainer/omarchy/lazygit.yml`.
- **starship** — while `~/.config/starship.toml` is empty, zsh points `STARSHIP_CONFIG` at `.devcontainer/omarchy/starship.toml`.
- **zsh** — Omarchy ships bash only, so `.devcontainer/zsh/interactive.zsh` ports its defaults to zsh (see below).

`.devcontainer/omarchy/VERSION` records which Omarchy release the files come from. To refresh them after an Omarchy update, run `.devcontainer/omarchy/sync.sh` on an Omarchy host, review the diff and commit.

### Interactive zsh

`.devcontainer/zsh/interactive.zsh` gives an Omarchy-style shell: `eza` for `ls`/`lt`, `zoxide` behind `cd`, `fzf` key bindings and `ff`, `bat` as `MANPAGER`, `EDITOR=nvim`, the `g`/`gcm`/`gcam`/`gcad`/`n`/`t`/`cx` aliases, and a `starship` prompt. The container hostname is fixed to `devcontainer` (`runArgs`), so a `user@host` prompt tells it apart from the host.

### Git over SSH

The host's gcr-ssh-agent socket directory is mounted at `/run/host-ssh`; private keys stay on the host. The host needs `systemctl --user enable --now gcr-ssh-agent.socket`. This mount is Linux-only: `initialize.d/07-ensure-host-mounts.sh` fails when `XDG_RUNTIME_DIR` is unset. On macOS, remove the `gcr` mount and `SSH_AUTH_SOCK` from `devcontainer.json`.
