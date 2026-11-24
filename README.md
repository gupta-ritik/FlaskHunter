# FlakeHunter

FlakeHunter is a Python 3.12 project for investigating flaky pytest tests from
GitHub Actions history.

In a Python 3.12 virtual environment with pip 25.1 or newer, run:

```sh
python -m pip install -e . --group dev
flakehunter --version
ruff check .
mypy src tests
pytest
```

## Run the local demo

```sh
flakehunter investigate --history tests/fixtures/slice/history --repo demo_repo
```

The demo test passes alone. Its predecessor mutates module-level options, so
running the predecessor first reproduces the captured `AssertionError`. The CLI
runs each condition in five fresh pytest processes and saves its report under
`reports/` in the current directory. The report includes the working directory,
exact replay arguments, and exit code, outcome, signature, and time for each
trial.

Two matching trigger failures paired with clean controls confirm order
dependence at 0.80 confidence. A single matched pair scores 0.50 and leaves
the cause unknown.
