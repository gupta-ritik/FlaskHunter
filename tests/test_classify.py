from flakehunter.classify import classify
from flakehunter.replay import Trial

SIGNATURE = "AssertionError: shared state was changed"


def _failure(signature: str | None = SIGNATURE) -> Trial:
    return Trial(exit_code=1, outcome="fail", signature=signature, elapsed_s=0.01)


def _pass() -> Trial:
    return Trial(exit_code=0, outcome="pass", signature=None, elapsed_s=0.01)


def test_classify_order_dependence_with_repeated_matches() -> None:
    result = classify(SIGNATURE, [_failure(), _failure()], [_pass(), _pass()])
    assert (result.cause, result.confidence) == ("order_dependence", 0.80)


def test_classify_unknown_when_control_also_fails() -> None:
    result = classify(SIGNATURE, [_failure(), _failure()], [_pass(), _failure()])
    assert result.cause == "unknown"


def test_classify_unknown_with_one_matched_pair() -> None:
    result = classify(SIGNATURE, [_failure()], [_pass()])
    assert (result.cause, result.confidence) == ("unknown", 0.50)


def test_classify_unknown_without_historical_signature() -> None:
    result = classify(None, [_failure(), _failure()], [_pass(), _pass()])
    assert (result.cause, result.confidence) == ("unknown", 0.0)


def test_classify_unknown_when_trigger_signature_differs() -> None:
    result = classify(SIGNATURE, [_failure("ValueError: different")], [_pass()])
    assert (result.cause, result.confidence) == ("unknown", 0.0)


def test_classify_unknown_without_any_completed_pairs() -> None:
    timeout = Trial(exit_code=None, outcome="timeout", signature=None, elapsed_s=1)
    result = classify(SIGNATURE, [_failure(), timeout], [timeout, _pass()])
    assert (result.cause, result.confidence) == ("unknown", 0.0)
