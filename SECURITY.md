# Security Policy

## Supported Versions

| Version | Supported |
| :--- | :---: |
| 2.1.x | Yes |
| 2.0.x | Yes |
| 1.1.x | Yes |
| < 1.1 | No |

Supported means confirmed vulnerabilities receive a fix in that line. Fixes for lines older than the latest minor release may be limited to the current release at the maintainer's discretion.

## Scope

In scope:

- Flask routes, request validation, and error handling in `src/`.
- API key authentication, rate limiting, and cache behavior.
- Security headers, CORS defaults, and proxy trust handling.
- Docker, Compose, and Helm defaults in `Dockerfile`, `docker-compose.yml`, and `deploy/`.

Out of scope:

- Vulnerabilities in ForexFactory, CryptoCraft, EnergyExch, MetalsMine, or their infrastructure.
- Vulnerabilities in the upstream [`forex-pytory`](https://github.com/AtaCanYmc/forex-pytory) parser. Report those to that repository.
- Missing hardening that requires a non-default configuration the documentation already warns about.

## Reporting a Vulnerability

Do not report security vulnerabilities through public GitHub issues, pull requests, or public discussions.

1. Email the maintainer at `atacanymc@gmail.com`.
2. Include the affected version or commit, the endpoint or component, reproduction steps, and the impact you can demonstrate.
3. Do not include live credentials, personal data, or data from third-party calendars in the report.

You will receive an acknowledgement within 48 hours. Validation and a fix depend on severity and reproducibility. A security advisory is published with the fix.

## Safe Harbor

Good-faith research is welcome when it:

- Avoids accessing, changing, or exfiltrating data that is not yours.
- Avoids denial of service, automated scraping at scale, and tests against third-party portals.
- Gives the maintainer reasonable time to release a fix before public disclosure.
- Complies with applicable law.

The maintainer will not pursue legal action for research that follows these rules.
