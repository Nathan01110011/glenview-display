.PHONY: lint format check

PY_DIRS=backend display-app

lint:
	.venv/bin/python -m pylint $(PY_DIRS)

format:
	ruff format $(PY_DIRS)

check: lint
	.venv/bin/ruff check $(PY_DIRS)
