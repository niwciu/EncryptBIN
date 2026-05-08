# 🤝 Contributing

---

## Prerequisites

- Python **3.10+**
- `git`
- `make` (Linux / macOS; Windows users run the commands manually)

---

## 🛠️ Set up the dev environment

```bash
git clone https://github.com/niwciu/encrypt-bin.git
cd encrypt-bin
make install
```

This creates `.venv/` and installs all dependencies (`.[gui,dev]`).

Without `make`:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[gui,dev]"
```

---

## ✅ Local checks

A `Makefile` provides shortcuts for every check that also runs in CI. Run `make help` to see all targets.

### Run everything at once

```bash
make check
```

This is equivalent to what CI runs: lint → format check → type check → security → tests. A pull request must pass all of these before it can merge.

### Individual targets

| Command | What it runs |
|---|---|
| `make lint` | `ruff check` + `flake8` |
| `make format` | `black` (auto-formats, modifies files) |
| `make format-check` | `black --check` (read-only, fails if formatting differs) |
| `make type-check` | `mypy src` |
| `make security` | `bandit -r src/ -ll` + `pip-audit` |
| `make test` | `pytest` with coverage (fails below 90%) |
| `make clean` | Remove `.venv/`, `dist/`, caches |

### Tool overview

| Tool | Purpose |
|---|---|
| **ruff** | Fast linter — catches style and logic issues |
| **flake8** | Secondary linter — enforces PEP 8 + complexity limits |
| **black** | Code formatter (line length 160) |
| **mypy** | Static type checker (`disallow_untyped_defs = true`) |
| **bandit** | Security scanner — flags medium/high severity issues in source code |
| **pip-audit** | Checks installed packages for known CVEs |
| **pytest** | Test runner with coverage reporting; minimum threshold is **90%** |

### Windows

Run the underlying commands directly in your activated venv:

```powershell
.venv\Scripts\pip install -e ".[gui,dev]"
.venv\Scripts\ruff check src/ tests/
.venv\Scripts\flake8 src tests
.venv\Scripts\mypy src
.venv\Scripts\black --check src tests
.venv\Scripts\bandit -r src/ -ll -x src/encrypt_bin/gui/resources
.venv\Scripts\pip-audit --skip-editable
$env:QT_QPA_PLATFORM="offscreen"; .venv\Scripts\pytest
```

---

## 🔬 Running tests

```bash
make test
# or directly:
QT_QPA_PLATFORM=offscreen .venv/bin/pytest
```

The test suite covers unit, integration, and end-to-end scenarios:

| File | What it tests |
|---|---|
| `test_builder.py` | Core binary generation function |
| `test_cli_parser.py` | CLI argument parsing and validation |
| `test_utils.py` | `parse_int`, `parse_key`, `find_key_in_file` |
| `test_validators.py` | File path and extension validation |
| `test_config.py` | Config value object |
| `test_e2e.py` | Full pipeline: parse → Config → generate → decrypt → verify |
| `test_gui.py` | GUI widget behaviour (offscreen Qt) |
| `test_main.py` | CLI entry point (`__main__.py`) |
| `test_main_edge.py` | Edge cases for the main entry point |

!!! tip "Coverage threshold"
    `pytest` is configured with `--cov-fail-under=90`. The suite currently achieves ≥ 93%. New behaviour must be accompanied by tests.

---

## 🗒️ CI

The CI pipeline (`.github/workflows/ci.yml`) runs the full matrix across **Python 3.10, 3.11, 3.12, and 3.13** (`fail-fast: false`) on every push and pull request. Build jobs for Linux and Windows binaries run after all lint + test steps pass.

---

## 📝 Changelog

Update `CHANGELOG.md` with every user-visible change before opening a PR. Add your entry under an `## Unreleased` section at the top (create it if it does not exist):

```markdown
## Unreleased

### Added
- Brief description of what changed and why
```

Use one of: `Added`, `Changed`, `Fixed`, `Removed`, `Security`. At release time the `Unreleased` block is renamed to the version and date.

---

## 🔀 Submitting a pull request

1. Fork the repository on GitHub.
2. Create a feature branch:
   ```bash
   git checkout -b feature/my-feature
   ```
3. Run `make check` locally before pushing — CI will run the same checks.
4. Update `CHANGELOG.md` under `## Unreleased`.
5. Open a pull request against `main` — the PR template will guide you through the checklist.

Keep PRs focused — **one feature or fix per PR**. Include tests for any new behaviour.
