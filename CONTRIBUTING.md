# Contributing to ForexFactoryScrapper

This document details development workflows, branch naming conventions, and testing requirements for submitting pull requests.

## Code of Conduct

All contributors are expected to adhere to the standards outlined in [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Issue Reporting

- Check existing issues before creating a new report.
- Include a descriptive title, reproduction steps, Python runtime version, operating system, and stack traces.

## Contribution Workflow

1. Fork the repository and create a feature branch from `main`:
   ```bash
   git checkout -b feat/my-feature
   ```
2. Implement your changes. Write pytest cases for any modified or new behavior.
3. Verify the test suite passes locally.
4. Keep commits scoped, adhering to Conventional Commits.
5. Open a pull request targeting `main`.

### Branch Naming Conventions

- `feat/<description>`: New endpoint or capability.
- `fix/<description>`: Bug fix or corrective change.
- `chore/<description>`: Dependency updates or build tooling.
- `docs/<description>`: Documentation additions or updates.

### Conventional Commit Specifications

All commit messages must follow the Conventional Commits format to facilitate automated release tagging and changelog updates via Release Please:

```text
<type>(<scope>): <description>

[optional body]
```

Example:
```text
feat(routes): add cryptocraft daily endpoint

Add endpoint and pagination unit tests for cryptocraft daily events.
```

## Local Development & Testing

1. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Execute automated test suite:
   ```bash
   python -m pytest -q
   ```

3. Run lint, the bandit scan, and tests together (mirrors CI):
   ```bash
   make install-dev && make check
   ```

4. Run the development server:
   ```bash
   python main.py
   ```
   The server binds to `http://127.0.0.1:5000` by default.

## Code Quality & Pre-commit

Install and run pre-commit hooks before pushing changes:

```bash
pre-commit install
pre-commit run --all-files
```

## API Specifications

Public API schemas are maintained in `src/openapi_spec.py`. When introducing or modifying endpoints, update this file so `/openapi.json` and the Swagger UI at `/swagger` reflect the accurate contract.

## Security Disclosures

Do not open public GitHub issues for security vulnerabilities. Refer to [SECURITY.md](SECURITY.md) for reporting guidelines.

