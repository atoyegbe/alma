# Makefile for Python project

# Variables
PYTHON := python3
PIP := pip
VENV := ./venv
SRC_DIR := app
TEST_DIR := tests
REQ_FILE := requirements.txt
COVERAGE_DIR := coverage

# Targets
.PHONY: all clean install test lint format coverage

all: install

run:
	bash run.sh

# Create and activate virtual environment, install dependencies
install: $(VENV)/bin/activate
	$(VENV)/bin/$(PIP) install -r $(REQ_FILE)

$(VENV)/bin/activate:
	$(PYTHON) -m venv $(VENV)

# Run tests
test:
	pytest $(TEST_DIR) -s

# Run linter (flake8)
lint:
	flake8 $(SRC_DIR) $(TEST_DIR)

# Format code (black)
format: pip install black
	black $(SRC_DIR)

# Generate test coverage report
coverage: install
	$(VENV)/bin/coverage run --source=$(SRC_DIR) -m pytest $(TEST_DIR)
	$(VENV)/bin/coverage report
	$(VENV)/bin/coverage html
	@echo "HTML report generated in $(COVERAGE_DIR)/index.html"

# Clean up build, virtual environment, and coverage files
clean:
	rm -rf $(VENV) $(COVERAGE_DIR) .pytest_cache .mypy_cache
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -exec rm -f {} +
