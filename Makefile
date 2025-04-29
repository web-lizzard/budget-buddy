.PHONY: run test add-dep remove-dep frontend-add-dep frontend-remove-dep

# Set PYTHONPATH to src
export PYTHONPATH := $(CURDIR)/backend/src

# Run main.py
run:
	cd backend && PYTHONPATH=$(PYTHONPATH) uv run src/main.py

# Run tests
test:
	cd backend && PYTHONPATH=$(PYTHONPATH) uv run pytest -vv

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

# Add frontend dependencies
frontend-add-dep:
	@read -p "Enter package name: " package; \
	cd frontend && npm install $$package

# Add frontend dev dependencies
frontend-add-dev-dep:
	@read -p "Enter development package name: " package; \
	cd frontend && npm install $$package --save-dev

# Remove frontend dependencies
frontend-remove-dep:
	@read -p "Enter package name to remove: " package; \
	cd frontend && npm uninstall $$package

help:
	@echo "Available commands:"
	@echo "  make run                - Run backend/src/main.py"
	@echo "  make test               - Run tests"
	@echo "  make add-dep            - Add dependency to the backend"
	@echo "  make add-dev-dep        - Add development dependency to the backend"
	@echo "  make remove-dep         - Remove dependency from the backend"
	@echo "  make frontend-add-dep   - Add dependency to the frontend"
	@echo "  make frontend-add-dev-dep - Add development dependency to the frontend"
	@echo "  make frontend-remove-dep  - Remove dependency from the frontend"
