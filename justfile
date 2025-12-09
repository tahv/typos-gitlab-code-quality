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
