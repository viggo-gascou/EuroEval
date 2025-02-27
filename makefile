# This ensures that we can call `make <target>` even if `<target>` exists as a file or
# directory.
.PHONY: help docs

# Exports all variables defined in the makefile available to scripts
.EXPORT_ALL_VARIABLES:

# Create .env file if it does not already exist
ifeq (,$(wildcard .env))
  $(shell touch .env)
endif

# Includes environment variables from the .env file
include .env

# Set gRPC environment variables, which prevents some errors with the `grpcio` package
export GRPC_PYTHON_BUILD_SYSTEM_OPENSSL=1
export GRPC_PYTHON_BUILD_SYSTEM_ZLIB=1

# Set the PATH env var used by cargo and uv
export PATH := ${HOME}/.local/bin:${HOME}/.cargo/bin:$(PATH)

# Set the shell to bash, enabling the use of `source` statements
SHELL := /bin/bash

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	@echo "Installing the 'ScandEval' project..."
	@$(MAKE) --quiet install-rust
	@$(MAKE) --quiet install-uv
	@$(MAKE) --quiet install-dependencies
	@$(MAKE) --quiet setup-environment-variables
	@$(MAKE) --quiet install-pre-commit
	@echo "Installed the 'ScandEval' project."

install-rust:
	@if [ "$(shell which rustup)" = "" ]; then \
		curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y; \
		echo "Installed Rust."; \
	fi

install-uv:
	@if [ "$(shell which uv)" = "" ]; then \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
        echo "Installed uv."; \
    else \
		echo "Updating uv..."; \
		uv self update; \
	fi

install-dependencies:
	@uv python install 3.11
	@uv sync --all-extras --python 3.11
	@if [ "${NO_FLASH_ATTN}" != "1" ] && [ $$(uname) != "Darwin" ]; then \
		uv pip install --no-build-isolation flash-attn>=2.7.0.post2; \
	fi
	@uv sync -U --only-dev

setup-environment-variables:
	@uv run python src/scripts/fix_dot_env_file.py

setup-environment-variables-non-interactive:
	@uv run python src/scripts/fix_dot_env_file.py --non-interactive

install-pre-commit:
	@uv run pre-commit install
	@uv run pre-commit autoupdate

docs:  ## View documentation locally
	@echo "Viewing documentation - run 'make publish-docs' to publish the documentation website."
	@uv run mkdocs serve

publish-docs:  ## Publish documentation to GitHub Pages
	@uv run mkdocs gh-deploy
	@echo "Updated documentation website: https://scandeval.com/"

test:  ## Run tests
	@uv run pytest && uv run readme-cov

tree:  ## Print directory tree
	@tree -a --gitignore -I .git .

lint:  ## Lint the project
	uv run ruff check . --fix --unsafe-fixes

format:  ## Format the project
	uv run ruff format .

type-check:  ## Type-check the project
	@uv run mypy . \
		--install-types \
		--non-interactive \
		--ignore-missing-imports \
		--show-error-codes \
		--check-untyped-defs

check: lint format type-check  ## Lint, format, and type-check the code

bump-major:
	@uv run python -m src.scripts.versioning --major
	@echo "Bumped major version!"

bump-minor:
	@uv run python -m src.scripts.versioning --minor
	@echo "Bumped minor version!"

bump-patch:
	@uv run python -m src.scripts.versioning --patch
	@echo "Bumped patch version!"

add-dev-version:
	@if [ $$(uname) = "Darwin" ]; then \
		sed -i '' 's/^version = "\(.*\)"/version = "\1.dev"/' pyproject.toml; \
	else \
		sed -i 's/^version = "\(.*\)"/version = "\1.dev"/' pyproject.toml; \
	fi
	@uv lock
	@git add pyproject.toml uv.lock
	@git commit -m "chore: Add '.dev' suffix to the version number"
	@git push
	@echo "Added '.dev' suffix to the version number."

publish:
	@if [ ${PYPI_API_TOKEN} = "" ]; then \
		echo "No PyPI API token specified in the '.env' file, so cannot publish."; \
	else \
		echo "Publishing to PyPI..."; \
		$(MAKE) --quiet check \
			&& uv build \
			&& uv publish --username "__token__" --password ${PYPI_API_TOKEN} \
			&& $(MAKE) --quiet publish-docs \
			&& $(MAKE) --quiet add-dev-version \
			&& echo "Published!"; \
	fi

publish-major: bump-major publish  ## Publish a major version

publish-minor: bump-minor publish  ## Publish a minor version

publish-patch: bump-patch publish  ## Publish a patch version
