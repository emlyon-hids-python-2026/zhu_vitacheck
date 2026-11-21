.PHONY: help install run_demo lint format clean

##################################################################################################################################################################################################
# Makefile for the project
##################################################################################################################################################################################################

help:  ## Show available commands
	@$(HELP_CMD)

install:  ## Install dependencies
	uv sync

run_demo:  ## Run the demo script
	uv run python scripts/demo.py

lint:  ## Check code with ruff
	uv run ruff check .

format:  ## Format code with ruff
	uv run ruff format .

clean:  ## Remove caches
	@$(CLEAN_CMD)

##################################################################################################################################################################################################
# Commands Help and Clean adapt to Windows and Unix-like systems
##################################################################################################################################################################################################

ifeq ($(OS),Windows_NT)
HELP_CMD = powershell -NoProfile -Command "Get-Content Makefile | ForEach-Object { if ($$_ -match '^([a-z0-9_-]+):.*?\#\# (.*)$$') { '  make {0,-12} {1}' -f $$Matches[1], $$Matches[2] } }"
else
HELP_CMD = grep -E '^[a-z0-9_-]+:.*\#\#' $(MAKEFILE_LIST) | awk -F':.*\#\# ' '{printf "  make %-12s %s\n", $$1, $$2}'
endif

ifeq ($(OS),Windows_NT)
CLEAN_CMD = powershell -NoProfile -Command "Get-ChildItem -Recurse -Directory -Force -Filter __pycache__ -ErrorAction SilentlyContinue | Where-Object { $$_.FullName -notmatch '[\\/]\.venv[\\/]' } | Remove-Item -Recurse -Force; Remove-Item -Recurse -Force -ErrorAction SilentlyContinue .mypy_cache, .ruff_cache, .venv"
else
CLEAN_CMD = find . -name __pycache__ -not -path "./.venv/*" -prune -exec rm -rf {} + ; rm -rf .mypy_cache .ruff_cache .venv
endif
