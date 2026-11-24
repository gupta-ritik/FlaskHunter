"""Deterministic classification for the order-dependence probe."""

from typing import Literal

from pydantic import BaseModel

from flakehunter.replay import Trial


class Classification(BaseModel):
    cause: Literal["order_dependence", "unknown"]
    confidence: float


def classify(
    signature: str | None, trigger: list[Trial], control: list[Trial]
) -> Classification:
    """Score paired evidence against the historical signature."""
    if (
        not signature
        or any(
            trial.outcome == "fail" and trial.signature != signature
            for trial in trigger
        )
        or any(trial.outcome == "fail" for trial in control)
    ):
        return Classification(cause="unknown", confidence=0.0)

    matches = sum(
        triggered.outcome == "fail" and baseline.outcome == "pass"
        for triggered, baseline in zip(trigger, control)
    )
    if matches >= 2:
        return Classification(cause="order_dependence", confidence=0.80)
    return Classification(cause="unknown", confidence=0.50 if matches == 1 else 0.0)
