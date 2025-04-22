.PHONY: run test add-dep remove-dep

# Set PYTHONPATH to src
export PYTHONPATH := $(CURDIR)/backend/src

# Run main.py
run:
	cd backend && PYTHONPATH=$(PYTHONPATH) uv run src/main.py

# Run tests
test:
	cd backend && PYTHONPATH=$(PYTHONPATH) uv run pytest

# Add dependencies
add-dep:
	@read -p "Enter package name: " package; \
	cd backend && uv add $$package

# Add development dependencies
add-dev-dep:
	@read -p "Enter development package name: " package; \
	cd backend && uv add $$package --group dev

# Remove dependencies
remove-dep:
	@read -p "Enter package name to remove: " package; \
	cd backend && uv remove $$package

help:
	@echo "Available commands:"
	@echo "  make run           - Run backend/src/main.py"
	@echo "  make test          - Run tests"
	@echo "  make add-dep       - Add dependency to the project"
	@echo "  make add-dev-dep   - Add development dependency"
	@echo "  make remove-dep    - Remove dependency from the project"
