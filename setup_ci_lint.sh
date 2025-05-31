#!/bin/bash
set -e

echo "🔧 Setting up CI and pre-commit linting for Spiral Codex..."

mkdir -p .github/workflows

cat > .github/workflows/ci.yml << 'EOF'
name: CI
on: [push, pull_request]
jobs:
  lint:
    name: Lint and Format
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python 3.8
        uses: actions/setup-python@v5
        with:
          python-version: "3.8"
      - name: Install dependencies
        run: pip install black ruff
      - name: Run Black
        run: black . --check
      - name: Run Ruff
        uses: astral-sh/ruff-action@v3
        with:
          args: "check --fix"

  test:
    name: Run Tests
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python 3.8
        uses: actions/setup-python@v5
        with:
          python-version: "3.8"
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run Pytest
        run: pytest tests/
EOF

cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black
        args: [--config=pyproject.toml]

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.7
    hooks:
      - id: ruff
        args: [--fix]
EOF

pip install pre-commit
pre-commit install

git add .github .pre-commit-config.yaml
git commit -m "🧪 Add CI workflow and pre-commit for Black + Ruff"
git push
