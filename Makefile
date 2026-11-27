.DEFAULT_GOAL := help
.PHONY: help init venv install install-dev run test lint format security check docker-build docker-run docker-stop docker-logs clean

VENV ?= .venv
# Use the virtualenv interpreter when it exists, otherwise fall back to the system one.
PYTHON ?= $(if $(wildcard $(VENV)/bin/python),$(VENV)/bin/python,python3)
IMAGE ?= forexfactory-scrapper
PORT ?= 5000

help: ## Show this help
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "  make %-14s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

venv: ## Create the virtualenv in .venv
	python3 -m venv $(VENV)

init: ## Interactive wizard that writes .env
	$(PYTHON) scripts/init_wizard.py

install: ## Install runtime and test dependencies
	$(PYTHON) -m pip install -r requirements.txt

install-dev: install ## Install lint and security tools (black, flake8, bandit)
	$(PYTHON) -m pip install black flake8 bandit

run: ## Start the API server locally
	$(PYTHON) main.py

test: ## Run the test suite
	$(PYTHON) -m pytest -q

lint: ## Run flake8 and black --check
	$(PYTHON) -m flake8
	$(PYTHON) -m black --check .

format: ## Auto-format with black
	$(PYTHON) -m black .

security: ## Run the bandit scan used in CI
	$(PYTHON) -m bandit -q -r src/

check: lint security test ## Run lint, security scan, and tests (mirrors CI)

docker-build: ## Build the Docker image
	docker build -t $(IMAGE) .

docker-run: ## Run the container in the background on PORT (default 5000)
	docker run -d -p $(PORT):5000 --name $(IMAGE) $(IMAGE)

docker-stop: ## Stop and remove the container
	-docker rm -f $(IMAGE)

docker-logs: ## Follow container logs
	docker logs -f $(IMAGE)

clean: ## Remove caches and build artifacts
	find . -type d -name "__pycache__" -not -path "./$(VENV)/*" -exec rm -rf {} +
	find . -type f -name "*.pyc" -not -path "./$(VENV)/*" -delete
	rm -rf .pytest_cache .coverage
