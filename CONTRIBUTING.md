# Contributing to ForexFactoryScrapper

Changes land through pull requests against `main`. This document covers setup, verification, commit format, and the review checklist.

## Requirements

- Python 3.10, 3.11, or 3.12.
- `make` for the local command wrappers.
- Docker and Helm are optional and only needed for container or chart changes.

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

2. Install dependencies and, optionally, the documented defaults:

   ```bash
   make install-dev
   cp .env.example .env
   ```

3. Implement your changes. Write pytest cases for any modified or new behavior.
4. Run `make check` and the pre-commit hooks.
5. Keep commits scoped and follow Conventional Commits.
6. Open a pull request targeting `main` and complete the template checklist.

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

2. Install the dev tools and run the full local gate (flake8, `black --check`, bandit, pytest):

   ```bash
   make install-dev
   make check
   ```

3. Run the development server:

   ```bash
   python main.py
   ```

   The server binds to `http://127.0.0.1:5000` by default. Copy `.env.example` to `.env` only when you need non-default settings.

## Continuous Integration

| Workflow | Checks |
| :--- | :--- |
| `ci.yml` | black, flake8, bandit, and pytest on Python 3.10 to 3.12. `helm lint` and `helm template` for the chart. Offline Bruno requests against a running API. |
| `well-document-gate.yml` | Required governance files, README slop and em-dash lint, internal link check. |
| `docs.yml` | Verifies and deploys `pages/` to GitHub Pages. |
| `release-please.yml` | Release PR, version bumps, tags. |

`make check` runs the lint, security, and test steps locally.

## Versioning & Releases

Release Please owns every version number. Do not edit versions by hand. On each merge to `main` it opens a release PR from Conventional Commits. Merging that PR bumps `version.txt`, `Chart.yaml` (`version` and `appVersion`), and `src/openapi_spec.py` together, updates `CHANGELOG.md`, and creates the `vX.Y.Z` tag. A follow-up job moves the floating `vX` tag. Configuration lives in `release-please-config.json` and `.release-please-manifest.json`. Add a new file to `extra-files` and mark its version line with `x-release-please-version` to bring it under the same control.

## Code Quality & Pre-commit

Install the hooks once, then run them before pushing:

```bash
pre-commit install
pre-commit run --all-files
```

## Documentation Sync

`README.md` is the user-facing reference. `pages/` is the published site, and `pages/llms.txt` is the machine-readable summary. When an endpoint, environment variable, limit, or response shape changes, update all of these together:

- `src/openapi_spec.py`
- `README.md` endpoint and configuration tables
- `.env.example`
- `pages/llms.txt`
- The matching request in `bruno/`

## API Specifications

Public API schemas are maintained in `src/openapi_spec.py`. When introducing or modifying endpoints, update this file so `/openapi.json` and the Swagger UI at `/swagger` reflect the accurate contract.

## Security Disclosures

Do not open public GitHub issues for security vulnerabilities. Refer to [SECURITY.md](SECURITY.md) for reporting guidelines.

## Pull Request Checklist

- [ ] New or changed behavior has a pytest case.
- [ ] `make check` passes.
- [ ] `pre-commit run --all-files` passes.
- [ ] Endpoint changes update `src/openapi_spec.py`, `README.md`, `pages/llms.txt`, and `bruno/`.
- [ ] Configuration changes update `.env.example` and the README table.
- [ ] No secrets, tokens, personal data, or local absolute paths are committed.
- [ ] Commit messages follow Conventional Commits.
