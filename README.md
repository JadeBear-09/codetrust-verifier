# CodeTrust

[![CI](https://github.com/JadeBear-09/codetrust-verifier/actions/workflows/ci.yml/badge.svg)](https://github.com/JadeBear-09/codetrust-verifier/actions/workflows/ci.yml)

Evidence-first verification for software pull requests. CodeTrust compares stated intent with changed code, runs deterministic risk gates, and emits traceable `BLOCK`, `NEEDS_REVIEW`, or `PASS` evidence. It never merges or deploys.

## Run

Requires Python 3.11 or newer. GitHub PR analysis also requires authenticated [GitHub CLI](https://cli.github.com/).

```bash
git clone https://github.com/JadeBear-09/codetrust-verifier.git
cd codetrust-verifier
python3 start.py
```

`start.py` installs dependencies, prepares offline evidence, starts dashboard, and opens <http://127.0.0.1:8787>.

Useful commands:

```bash
python3 start.py --setup-only  # Install without starting server
python3 start.py --check       # Run tests and lint
python3 start.py --no-open     # Start without opening browser
```

## Gemini setup

CodeTrust works offline without API credentials. Gemini adds intent synthesis; deterministic findings and verdict remain unchanged.

```bash
cp .env.example .env
# Put Gemini API key in .env, then:
python3 start.py
```

Default model: `gemini-3.5-flash`. Override with `CODETRUST_MODEL`. `.env` is ignored by Git and Docker.

## Verify pull request

```bash
uv run codetrust verify \
  --github-pr OWNER/REPOSITORY#123 \
  --ticket path/to/scope.md \
  --output-dir reports
```

Use full GitHub PR URL instead of `OWNER/REPOSITORY#123` in dashboard. CodeTrust fetches metadata and diff through fixed `gh` commands; it never checks out or runs PR code.

Generated evidence:

- `latest.html` — human decision view
- `latest.md` — review-ready report
- `latest.json` — hashed machine-readable result
- `adversarial-tests.md` — suggested verification cases

Exit code `1` means `BLOCK`, suitable for CI policy gates.

## Rejection demos

Public GnuCash PR rejected by maintainers as out of scope:

```bash
make demo-real-pr
```

Expected: `BLOCK · risk 100/100`, followed by `EXTERNAL MATCH`.

Any PR against this repository, checked against committed repository scope:

```bash
make demo-pr PR=JadeBear-09/codetrust-verifier#1
```

Expected demo PR adds weather-dashboard code. Policy explicitly marks weather features out of scope, so CodeTrust returns `BLOCK` with file, line, evidence, impact, and suggested verification.

## Local diff

```bash
uv run codetrust verify \
  --ticket demo/tickets/payment-reconciliation.md \
  --diff demo/patches/risky-payment.diff \
  --offline
```

## Safety boundary

- Ticket, diff, PR metadata, and model output are untrusted data.
- Deterministic evidence stays separate from model interpretation.
- Commands found inside tickets or diffs are never executed.
- `PASS` means no configured gate blocked change; it does not prove safety.
- API keys stay local in ignored `.env` files.

See [SECURITY.md](SECURITY.md) for threat model and production requirements.

## Development

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
```

## License

MIT
