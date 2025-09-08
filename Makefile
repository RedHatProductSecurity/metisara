# Metisara Development Makefile

.PHONY: help install install-dev test lint format type-check clean build upload docs

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install package dependencies"
	@echo "  install-dev  - Install package + development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run linting (flake8)"
	@echo "  format       - Format code (black)"
	@echo "  format-check - Check code formatting"
	@echo "  type-check   - Run type checking (mypy)"
	@echo "  security     - Run security checks"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build package"
	@echo "  check-all    - Run all checks (lint, format, type, test)"
	@echo "  setup        - Initial setup for development"
	@echo "  podman-test  - Run tests in Podman container"
	@echo "  podman-shell - Open shell in Podman container"
	@echo "  podman-clean - Clean up Podman containers and images"

# Installation
install:
	pip install -r requirements.txt
	pip install -e .

install-dev:
	pip install -r requirements.txt
	pip install -e .
	pip install pytest pytest-cov black flake8 mypy bandit safety twine build

# Testing
test:
	pytest tests/

test-cov:
	pytest tests/ --cov=src/metisara --cov-report=html --cov-report=term

# Code quality
lint:
	flake8 src/ tests/ --max-line-length=100

format:
	black src/ tests/

format-check:
	black --check src/ tests/

type-check:
	mypy src/metisara/ --ignore-missing-imports

security:
	bandit -r src/
	safety check

# All checks
check-all: lint format-check type-check test

# Clean up
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	./metis --clean

# Build
build: clean
	python -m build

# Development setup (macOS/Fedora)
setup:
	@echo "Setting up development environment for macOS/Fedora..."
	@if [ ! -f metisara.conf ]; then \
		cp examples/metisara.conf.example metisara.conf; \
		echo "Created metisara.conf from example"; \
	fi
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env from example - please edit with your API token"; \
	fi
	@echo "Setup complete! Edit metisara.conf and .env with your settings."
	@echo "Supported platforms: macOS, Fedora Linux"

# Development workflow
dev-check: format lint type-check test
	@echo "All checks passed! ✅"

# Release preparation
pre-release: clean check-all build
	@echo "Package ready for release! 🚀"

# Local testing
test-dry-run:
	./metis --dry-run

test-config:
	./metis --generate-config

# Container testing
podman-test:
	./podman-scripts.sh build
	./podman-scripts.sh start
	podman exec metisara-pod-metisara-fedora /bin/bash -c "source venv/bin/activate && ./metis --version && ./metis --dry-run"

podman-shell:
	./podman-scripts.sh start
	./podman-scripts.sh exec metisara-fedora

podman-clean:
	./podman-scripts.sh cleanup