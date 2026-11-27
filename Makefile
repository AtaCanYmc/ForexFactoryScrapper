.PHONY: help install run test lint format docker-build docker-run clean

PYTHON ?= python3
PIP ?= pip

help:
	@echo "Available targets:"
	@echo "  make install      Install application dependencies"
	@echo "  make run          Start the API server locally"
	@echo "  make test         Execute test suite via pytest"
	@echo "  make lint         Run linters (flake8, black check)"
	@echo "  make format       Auto-format codebase with black"
	@echo "  make docker-build Build Docker image"
	@echo "  make docker-run   Run Docker container"
	@echo "  make clean        Remove cache and temporary build artifacts"

install:
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) main.py

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m flake8
	$(PYTHON) -m black --check .

format:
	$(PYTHON) -m black .

docker-build:
	docker build -t forexfactory-scrapper .

docker-run:
	docker run -d -p 5000:5000 --name forexfactory-scrapper forexfactory-scrapper

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache site .coverage
