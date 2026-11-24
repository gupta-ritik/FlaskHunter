"""Shared request options for the synthetic order-dependence case."""

DEFAULT_OPTIONS: dict[str, str] = {}


def options_for(output_format: str) -> dict[str, str]:
    return DEFAULT_OPTIONS | {"format": output_format}
