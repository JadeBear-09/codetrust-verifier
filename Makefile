.PHONY: setup start check install test lint demo demo-offline demo-real-pr demo-pr proof serve clean

setup:
	python3 start.py --setup-only --no-open

start:
	python3 start.py

check:
	python3 start.py --check

install:
	uv sync --extra dev

test:
	uv run pytest

lint:
	uv run ruff check .

demo:
	uv run codetrust verify --ticket demo/tickets/payment-reconciliation.md --diff demo/patches/risky-payment.diff --output-dir reports

demo-offline:
	uv run codetrust verify --offline --ticket demo/tickets/payment-reconciliation.md --diff demo/patches/risky-payment.diff --output-dir reports

demo-real-pr:
	uv run python -m codetrust.real_pr_demo

demo-pr:
	@test -n "$(PR)" || (echo "Usage: make demo-pr PR=OWNER/REPO#NUMBER" && exit 2)
	@uv run codetrust verify --github-pr "$(PR)" --ticket demo/policies/codetrust-scope.md --offline --output-dir reports/public-pr; \
	code=$$?; \
	if [ $$code -eq 1 ]; then echo "Expected demo result: BLOCK"; exit 0; fi; \
	echo "Unexpected demo exit code: $$code"; exit 1

proof:
	uv run python scripts/prove_demo.py

serve:
	uv run codetrust serve

clean:
	rm -f reports/*.json reports/*.md reports/*.html
