.PHONY: all
all: build

.PHONY: build
build: ## Build package
	python -m pip install --upgrade build
	python -m build        
	twine check dist/*

.PHONY: direnv
direnv:
	[ -n "${DIRENV_DIR}" ] || ( echo Please activate direnv by typing "direnv allow ." && exit 1 )

.PHONY: install
install: ## Install Python requirements
	python -m pip install --upgrade pip setuptools wheel
	python -m pip install -r ./requirements.txt

.PHONY: upgrade
upgrade: ## Upgrade Python requirements to latest version
	python -m pur -r requirements.txt
	python -m pip install --upgrade -r ./requirements.txt
	python -m pur -r requirements-docs.txt
	python -m pip install --upgrade -r ./requirements-docs.txt
	python -m pur -r requirements-dev.txt
	python -m pip install --upgrade -r ./requirements-dev.txt

.PHONY: clean
clean: ## Clean generated data
	find . -name .mypy_cache -or -name __pycache__ -or -name .pytest_cache -or -name aldegonde.egg-info -print0 | xargs -0 rm -rf

.PHONY: lint
lint: ## Various Linters
	yamllint .github

# Thanks to Francoise at marmelab.com for this
.DEFAULT_GOAL := help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
