# CodeTrust

[![CI](https://github.com/JadeBear-09/codetrust-verifier/actions/workflows/ci.yml/badge.svg)](https://github.com/JadeBear-09/codetrust-verifier/actions/workflows/ci.yml)

CodeTrust checks whether a pull request matches approved product scope. It returns a traceable verdict with file, line, evidence, impact, and suggested verification for every finding.

CodeTrust does **not** merge, deploy, or claim that passing checks proves safety.

## What goes in and what comes out

You provide:

1. A GitHub pull-request link or unified diff.
2. A scope file describing approved and forbidden work.

CodeTrust produces:

- `PASS` — no configured gate blocked the change.
- `NEEDS_REVIEW` — evidence requires human judgment.
- `BLOCK` — a hard gate failed, including explicit out-of-scope work.
- HTML, Markdown, and JSON evidence reports under `reports/`.

```text
Pull request + approved scope
              │
              ▼
     deterministic verification
              │
              ▼
   PASS / NEEDS_REVIEW / BLOCK
              │
              ▼
       evidence-backed report
```

## Fastest start: local dashboard

Requirement: Python 3.11 or newer.

```bash
git clone https://github.com/JadeBear-09/codetrust-verifier.git
cd codetrust-verifier
python3 start.py
```

This command installs dependencies, creates offline demo evidence, starts CodeTrust, and opens <http://127.0.0.1:8787>.

No API key is required for offline verification.

## Run rejection demos

These commands require [`uv`](https://docs.astral.sh/uv/) and authenticated [GitHub CLI](https://cli.github.com/):

```bash
uv sync
gh auth status          # Run `gh auth login` if needed
```

### Demo 1: public GnuCash rejection

```bash
make demo-real-pr
```

Expected result:

```text
BLOCK · risk 100/100
EXTERNAL MATCH
```

CodeTrust checks [GnuCash PR #2262](https://github.com/Gnucash/gnucash/pull/2262) against explicit GTK3 theme ownership. Maintainer independently closed that PR as out of scope.

### Demo 2: tested code outside this repository's scope

```bash
make demo-pr PR=JadeBear-09/codetrust-verifier#1
```

Expected result:

```text
BLOCK · risk 45/100 · 2 findings
Expected demo result: BLOCK
```

PR #1 adds a weather dashboard. Its tests and CI pass, but repository policy explicitly forbids weather features. CodeTrust blocks both changed files; PR remains closed and unmerged.

## Analyze your own GitHub pull request

### 1. Create a scope file

Save this as `scope.md` and replace example text:

```markdown
# Repository scope

## Outcome
Describe intended product outcome.

## In scope
- Describe approved work.

## Out of scope
- Describe forbidden or unrelated work.

## Acceptance criteria
- Describe evidence required for approval.
```

### 2. Run verification

```bash
uv run codetrust verify \
  --github-pr OWNER/REPOSITORY#123 \
  --ticket scope.md \
  --offline \
  --output-dir reports
```

Replace `OWNER/REPOSITORY#123` with target PR. GitHub PR URL also works.

`--offline` disables model synthesis. Deterministic rules, risk score, and verdict still run.

### 3. Open evidence

```bash
open reports/latest.html       # macOS
xdg-open reports/latest.html   # Linux
```

Generated files:

- `latest.html` — visual decision report.
- `latest.md` — review-ready evidence.
- `latest.json` — machine-readable result with evidence hash.
- `adversarial-tests.md` — suggested verification cases.

CLI exits with code `1` for `BLOCK`. This is intentional and lets CI stop unsafe changes.

## Analyze a local diff

```bash
uv run codetrust verify \
  --ticket demo/tickets/payment-reconciliation.md \
  --diff demo/patches/risky-payment.diff \
  --offline \
  --output-dir reports
```

## Optional Gemini synthesis

Gemini explains intent and unresolved questions. It cannot change deterministic findings or verdict.

```bash
cp .env.example .env
```

Then edit `.env`:

```dotenv
GEMINI_API_KEY=replace_with_your_gemini_api_key
CODETRUST_MODEL=gemini-3.5-flash
```

Remove `--offline` when running verification. `.env` is excluded from Git and Docker.

## Safety guarantees

- Ticket text, diffs, PR metadata, and model output are treated as untrusted data.
- Commands found inside tickets or diffs are never executed.
- GitHub ingestion uses fixed `gh` argument lists; CodeTrust never checks out PR code.
- Deterministic evidence stays separate from model interpretation.
- `PASS` means configured gates found no blocker. It does not prove safety.

See [SECURITY.md](SECURITY.md) for threat model and production requirements.

## Useful commands

```bash
python3 start.py --setup-only  # Install and prepare demo evidence
python3 start.py --check       # Run tests and lint
python3 start.py --no-open     # Start without opening browser
uv run pytest                  # Run tests
uv run ruff check .            # Run lint
```

## License

MIT
