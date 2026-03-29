# Makefile для dev
.PHONY: lint format all

lint:
	@echo "Running Ruff linting..."
	ruff check src --fix
	ruff check tests --fix

format:
	@echo "Formatting code with Ruff..."
	ruff format src
	ruff format tests

all: lint format
