.PHONY: install test lint typecheck format check build clean help

install: ## Install the package with development dependencies, editable
	python -m pip install --upgrade pip
	python -m pip install -e ".[dev]"

test: ## Run the test suite
	python -m pytest tests/aldegonde

lint: ## Lint and check formatting with ruff
	ruff check src tests experiments
	ruff format --check src tests experiments

typecheck: ## Type-check the library with ty
	ty check src

format: ## Format with ruff
	ruff format src tests experiments

check: lint typecheck test ## Everything CI runs, on this interpreter

build: ## Build the distribution and check it
	python -m pip install --upgrade build twine
	python -m build
	twine check dist/*

clean: ## Remove build and tool caches
	rm -rf build dist .tox .coverage htmlcov .pytest_cache .ruff_cache .hypothesis
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
	find . -name '*.egg-info' -type d -prune -exec rm -rf {} +

.DEFAULT_GOAL := help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-12s\033[0m %s\n", $$1, $$2}'
