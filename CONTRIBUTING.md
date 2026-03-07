# Contributing to ForexFactoryScrapper

Thanks for your interest in contributing! This document explains the preferred workflow and standards for contributing code, tests, docs, or fixes to this repository.

Please follow these steps to make the process smooth and fast for everyone:

## Code of conduct
Be respectful and constructive. If you have any concerns about community behavior, contact the maintainer: atacanymc@gmail.com.

## Report an issue
- Search existing issues before opening a new one.
- When opening an issue, provide a clear title and reproducible steps, environment (OS, Python version), and logs or error messages if applicable.

## How to contribute
1. Fork the repository and create a feature branch from `main`:

   ```bash
   git checkout -b feat/my-feature
   ```

2. Write tests for any new behavior or bugfix (prefer pytest).
3. Run the test suite locally and make sure all tests pass.
4. Keep commits small and focused. Use clear commit messages.
5. Open a pull request against the `main` branch and describe the change and why it is needed.

### Branch naming conventions
- `feat/<short-description>` — new features
- `fix/<short-description>` — bug fixes
- `chore/<short-description>` — maintenance tasks
- `docs/<short-description>` — documentation-only changes

### Commit message style
Keep messages short and descriptive. Example:

```
feat(routes): add cryptocraft daily endpoint

Add new endpoint and tests that validate paging behavior.
```

## Pull request checklist
Before requesting review, ensure the following:
- [ ] The PR targets `main` (or the branch specified by the maintainers).
- [ ] Tests were added or updated for new behavior.
- [ ] All tests pass locally: `python -m pytest -q`.
- [ ] The `README.md` and `src/openapi_spec.py` are updated if public APIs changed.
- [ ] If appropriate, run `pre-commit` hooks locally: `pre-commit run --all-files`.

## Testing locally
- Create and activate a virtualenv:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- Run tests:

```bash
python -m pytest -q
```

- Run the app locally for manual testing:

```bash
python main.py
# then open http://localhost:5000/ in your browser
```

## Linting / formatting
- This repository includes `pre-commit` in `requirements.txt`. Install and run hooks:

```bash
pre-commit install
pre-commit run --all-files
```

If you don’t have `pre-commit` installed globally, you can run it from the virtualenv: `python -m pre_commit run --all-files`.

## Documentation and OpenAPI
- The OpenAPI spec is maintained in `src/openapi_spec.py`. If you add or change public endpoints or response formats, please update that file so `/openapi.json` and the Swagger UI remain accurate.
- Update `README.md` for any end-user visible change.

## Security
- Do not commit secrets or credentials. Use environment variables or `.env` files excluded via `.gitignore`.
- If you discover a security vulnerability, contact the maintainer privately at atacanymc@gmail.com before opening a public issue.

## Getting help
If you need guidance on where to start, open an issue titled `help wanted` with what you’d like to work on — the maintainer or contributors will respond with suggestions.

Thank you for contributing and helping improve ForexFactoryScrapper!
