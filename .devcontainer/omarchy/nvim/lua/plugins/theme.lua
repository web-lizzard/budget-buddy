-- Not part of omarchy-nvim: on Omarchy this file is a symlink to the current theme's
-- neovim.lua. Load it from the mounted theme directory when the host has one; otherwise
-- LazyVim keeps its default colorscheme.
local theme = vim.fn.expand("~/.local/state/omarchy/current/theme/neovim.lua")
if vim.uv.fs_stat(theme) then
	return dofile(theme)
end
return {}
