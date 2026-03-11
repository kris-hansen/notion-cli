.PHONY: setup install dev test lint format build clean

# Create virtual environment and install dependencies
setup:
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -e ".[dev]"

# Install in development mode
install:
	pip install -e .

# Install with dev dependencies
dev:
	pip install -e ".[dev]"

# Run tests
test:
	pytest tests/ -v

# Run linters
lint:
	ruff check notioncli/
	black --check notioncli/

# Format code
format:
	black notioncli/
	isort notioncli/
	ruff check --fix notioncli/

# Build standalone executable
build:
	pyinstaller --onefile --name notion cli.py

# Clean build artifacts
clean:
	rm -rf build/ dist/ *.spec
	rm -rf __pycache__ notioncli/__pycache__
	rm -rf *.egg-info
	rm -rf .pytest_cache .ruff_cache
	find . -name "*.pyc" -delete
