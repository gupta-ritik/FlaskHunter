# FlakeHunter

FlakeHunter is a Python 3.12 project for investigating flaky pytest tests from
GitHub Actions history. The current scaffold provides a versioned CLI.

In a Python 3.12 virtual environment with pip 25.1 or newer, run:

```sh
python -m pip install -e . --group dev
flakehunter --version
ruff check .
mypy src tests
pytest
```
