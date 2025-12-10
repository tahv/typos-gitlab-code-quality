GITHUB_SERVER_URL := env("GITHUB_SERVER_URL", "https://github.com")
GITHUB_REPOSITORY := env("GITHUB_REPOSITORY", "tahv/typos-gitlab-code-quality")

# List available recipes
[default, private]
list:
  @just --list

# Sync project
sync:
  uv sync

# Build Python wheel and sdist
build:
  uv build --no-sources

# Print project version
version:
  @uvx --with setuptools_scm setuptools-scm

# Run `ruff` linter
lint *files:
  uvx ruff check --output-format concise {{files}}

# Check typos
typos:
  uvx typos

# Run `mypy` type checker
mypy:
  uv run -m mypy

# Run test suite
test *args:
  uv run -m pytest {{args}}

# Run test suite and report coverage
coverage *args:
  uv run -m coverage erase
  uv run -m coverage run --parallel -m pytest {{args}}
  uv run -m coverage combine
  uv run -m coverage report

# Create a news fragment
news filename="":
  uvx towncrier create --no-edit {{ filename }}

# Build changelog from news fragments, or print a draft if `version` is not set
changelog version="":
  uvx towncrier build {{ if version == "" { "--draft --version 0.0.0" } else { "--version " + version } }}

# Output `version` release notes from CHANGELOG.md
release-notes version:
  @uv run scripts/release-notes.py \
    --version "{{ version }}" \
    --diff-url "$GITHUB_SERVER_URL/$GITHUB_REPOSITORY/compare/{old}...{new}"
