from demo_state import DEFAULT_OPTIONS, options_for


def test_changes_state() -> None:
    DEFAULT_OPTIONS["format"] = "json"
    assert options_for("json")["format"] == "json"


def test_starts_clean() -> None:
    assert not DEFAULT_OPTIONS, "shared state was changed"


def test_explicit_format() -> None:
    assert options_for("text")["format"] == "text"
