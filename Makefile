PYTHON ?= python3
VENV := .venv/bin

.PHONY: setup test lint dev-backend dev-frontend privacy hooks
setup:
	$(PYTHON) -m venv --copies .venv
	$(VENV)/python -m pip install -r requirements-dev.lock
	$(VENV)/python -m pip install --no-deps --no-build-isolation -e .
	npm --prefix frontend ci

test:
	$(VENV)/python -m pytest
	npm --prefix frontend test
	npm --prefix frontend run build
	$(MAKE) privacy

lint:
	$(VENV)/ruff check backend ml tests scripts
	$(VENV)/ruff format --check backend ml tests scripts
	npm --prefix frontend run lint

dev-backend:
	$(VENV)/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload --no-access-log

dev-frontend:
	npm --prefix frontend run dev -- --host 127.0.0.1

privacy:
	$(PYTHON) scripts/check_repository.py --worktree
	$(PYTHON) scripts/check_repository.py --history

hooks:
	git config core.hooksPath .githooks
