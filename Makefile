.PHONY: all
all: build

.PHONY: build
build: ## Build package
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
	pur
	python -m pip pip install --upgrade -r ./requirements.txt

.PHONY: clean
clean: ## Clean Jupyter Notebooks of output data
	find notebooks -name '*.ipynb' | xargs -P 6 -n 1 jupyter nbconvert --clear-output --inplace

.PHONY: lint
lint: ## Various Linters
	yamllint .github

# Thanks to Francoise at marmelab.com for this
.DEFAULT_GOAL := help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
