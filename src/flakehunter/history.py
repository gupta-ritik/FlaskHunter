"""Load local JUnit history and find flaky pytest tests."""

import json
import re
import warnings
from collections import defaultdict
from pathlib import Path
from typing import Annotated, Literal, NamedTuple
from xml.etree import ElementTree

from pydantic import (
    BaseModel,
    ConfigDict,
    PositiveInt,
    StringConstraints,
    ValidationError,
)

Outcome = Literal["pass", "fail", "skip", "error"]
NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class HistoryWarning(UserWarning):
    """Part of the local history could not be loaded."""


class HistoryRow(BaseModel):
    """One normalized testcase observation."""

    model_config = ConfigDict(frozen=True)

    run_id: int
    attempt: int
    job_key: str
    env_key: str
    head_sha: str
    node_id: str
    outcome: Outcome
    signature: str | None
    source_url: str


class Candidate(BaseModel):
    """A test with both outcomes across comparable attempts."""

    node_id: str
    head_sha: str
    job_key: str
    env_key: str
    passes: int
    fails: int
    signatures: list[str]


class _Environment(BaseModel):
    python: NonEmptyString
    os: NonEmptyString


class _AttemptMetadata(BaseModel):
    model_config = ConfigDict(strict=True)

    repo: NonEmptyString
    head_sha: NonEmptyString
    workflow: NonEmptyString
    job: NonEmptyString
    env: _Environment
    run_id: PositiveInt
    attempt: PositiveInt
    artifact_url: NonEmptyString


_EXCEPTION_NAME = r"[A-Z]\w*(?:\.[A-Za-z_]\w*)*|(?:[a-z_]\w*\.)+[A-Z]\w*"
_MESSAGE_TYPE = re.compile(rf"^({_EXCEPTION_NAME})(?::|$)")
_TRACEBACK_TYPE = re.compile(rf"^.*:\d+:\s+({_EXCEPTION_NAME})(?::|$)", re.MULTILINE)


def _node_id(testcase: ElementTree.Element) -> str | None:
    property_element = testcase.find("properties/property[@name='nodeid']")
    if property_element is not None:
        node_id = property_element.get("value") or property_element.text
        if node_id:
            return node_id

    name = testcase.get("name")
    classname = testcase.get("classname", "")
    if not name:
        return None

    filename = testcase.get("file", "").replace("\\", "/")
    if filename:
        module = filename.removesuffix(".py").replace("/", ".")
        if classname == module or not classname:
            return f"{filename}::{name}"
        if classname.startswith(module + "."):
            classes = classname[len(module) + 1 :].replace(".", "::")
            return f"{filename}::{classes}::{name}"

    if not classname:
        return None
    parts = classname.split(".")
    # Default pytest XML flattens both directories and classes into one dotted name.
    class_start = next(
        (i for i, part in enumerate(parts[1:], start=1) if part[:1].isupper()),
        len(parts),
    )
    module_path = "/".join(parts[:class_start]) + ".py"
    return "::".join([module_path, *parts[class_start:], name])


def _signature(detail: ElementTree.Element) -> str | None:
    lines = detail.get("message", "").strip().splitlines()
    message = lines[0].rstrip() if lines else ""
    exception_type = detail.get("type")
    if not exception_type:
        traceback_types = _TRACEBACK_TYPE.findall(detail.text or "")
        if traceback_types:
            exception_type = traceback_types[-1]
    prefix = _MESSAGE_TYPE.match(message)
    if prefix and exception_type in (None, prefix[1]):
        exception_type = prefix[1]
        message = message[prefix.end() :].lstrip()
    return ": ".join(part for part in (exception_type, message) if part) or None


def _result(testcase: ElementTree.Element) -> tuple[Outcome, str | None]:
    error = testcase.find("error")
    if error is not None:
        return "error", _signature(error)
    failure = testcase.find("failure")
    if failure is not None:
        return "fail", _signature(failure)
    if testcase.find("skipped") is not None:
        return "skip", None
    return "pass", None


class JUnitObservation(NamedTuple):
    node_id: str
    outcome: Outcome
    signature: str | None


def read_junit(path: Path) -> list[JUnitObservation]:
    """Read observations in the order recorded in a pytest JUnit report."""
    observations = []
    for testcase in ElementTree.parse(path).getroot().iter("testcase"):
        node_id = _node_id(testcase)
        if node_id is not None:
            outcome, signature = _result(testcase)
            observations.append(JUnitObservation(node_id, outcome, signature))
    return observations


def load_history(path: Path | str) -> list[HistoryRow]:
    """Read attempt folders and emit HistoryWarning for unavailable input."""
    path = Path(path)
    try:
        folders = sorted(path.iterdir())
    except OSError as exc:
        warnings.warn(
            f"Cannot read history at {path}: {exc.strerror}",
            HistoryWarning,
            stacklevel=2,
        )
        return []

    rows = []
    for folder in folders:
        if not folder.is_dir():
            continue
        metadata_path = folder / "metadata.json"
        try:
            metadata = _AttemptMetadata.model_validate_json(
                metadata_path.read_text(encoding="utf-8-sig")
            )
        except OSError as exc:
            warnings.warn(
                f"{metadata_path}: {exc.strerror}", HistoryWarning, stacklevel=2
            )
            continue
        except (UnicodeError, ValidationError):
            warnings.warn(
                f"{metadata_path}: invalid metadata", HistoryWarning, stacklevel=2
            )
            continue
        if folder.name != f"{metadata.run_id}-{metadata.attempt}":
            warnings.warn(
                f"{metadata_path}: run_id and attempt do not match the folder name",
                HistoryWarning,
                stacklevel=2,
            )
            continue

        reports = sorted(folder.glob("*.xml"))
        if not reports:
            warnings.warn(f"{folder}: no JUnit XML files", HistoryWarning, stacklevel=2)
            continue

        job_key = json.dumps(
            (metadata.repo, metadata.workflow, metadata.job), separators=(",", ":")
        )
        env_key = metadata.env.model_dump_json()
        for report in reports:
            try:
                observations = read_junit(report)
            except (OSError, ElementTree.ParseError, LookupError, ValueError) as exc:
                warnings.warn(
                    f"{report}: cannot read JUnit XML ({exc})",
                    HistoryWarning,
                    stacklevel=2,
                )
                continue
            for observation in observations:
                rows.append(
                    HistoryRow(
                        run_id=metadata.run_id,
                        attempt=metadata.attempt,
                        job_key=job_key,
                        env_key=env_key,
                        head_sha=metadata.head_sha,
                        node_id=observation.node_id,
                        outcome=observation.outcome,
                        signature=observation.signature,
                        source_url=metadata.artifact_url,
                    )
                )

    return list(dict.fromkeys(rows))


def detect_candidates(rows: list[HistoryRow]) -> list[Candidate]:
    """Count unique pass and fail attempts within each comparable group."""
    groups: dict[tuple[str, str, str, str], dict[tuple[int, int], list[HistoryRow]]] = (
        defaultdict(lambda: defaultdict(list))
    )
    for row in rows:
        group_key = row.node_id, row.head_sha, row.job_key, row.env_key
        groups[group_key][row.run_id, row.attempt].append(row)

    candidates = []
    for (node_id, head_sha, job_key, env_key), attempts in sorted(groups.items()):
        passes = 0
        fails = 0
        signatures: set[str] = set()
        for observations in attempts.values():
            outcomes = {row.outcome for row in observations}
            if outcomes == {"pass"}:
                passes += 1
            elif outcomes == {"fail"}:
                fails += 1
                signatures.update(
                    row.signature for row in observations if row.signature is not None
                )
        if passes and fails:
            candidates.append(
                Candidate(
                    node_id=node_id,
                    head_sha=head_sha,
                    job_key=job_key,
                    env_key=env_key,
                    passes=passes,
                    fails=fails,
                    signatures=sorted(signatures),
                )
            )
    return candidates
