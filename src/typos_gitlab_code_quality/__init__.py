# pyright: reportUnusedCallResult=false
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Literal, NotRequired, TypedDict, cast

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence


class TypoIssue(TypedDict):
    """Typos json output.

    https://github.com/crate-ci/typos/blob/213329406d908367bf5cab5e617b1c918c2f4b75/crates/typos-cli/src/report.rs#L75-L85
    """

    type: Literal["typo"]
    byte_offset: int
    typo: str
    corrections: list[str]
    line_num: NotRequired[int]  # FileContext only
    path: str  # FileContext & PathContext
    # buffer: list[int] ?


class GitlabIssue(TypedDict):
    """Code quality report format.

    https://docs.gitlab.com/ci/testing/code_quality/#code-quality-report-format
    """

    description: str
    """A human-readable description of the code quality violation."""

    check_name: str
    """A unique name representing the check, or rule, associated with this violation."""

    fingerprint: str
    """A unique fingerprint to identify this specific code quality violation,
    such as a hash of its contents.
    """

    severity: Literal["info", "minor", "major", "critical", "blocker"]
    """The severity of the violation."""

    location: GitlabIssueLocation


class GitlabIssueLines(TypedDict):
    begin: int
    """The line on which the code quality violation occurred."""


class GitlabIssueLocation(TypedDict):
    path: str
    """The file containing the code quality violation,
    expressed as a relative path in the repository.
    Do not prefix with `./`.
    """

    lines: GitlabIssueLines


def main(args: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "infile",
        nargs="?",
        default="-",
        help="Input file, default to stdin",
    )

    namespace = parser.parse_args(args)
    infile = cast("str", namespace.infile)

    if infile == "-":
        result = _parse_lines(sys.stdin.buffer)
    else:
        with Path(infile).open("rb") as f:
            result = _parse_lines(f)

    print(json.dumps(result), end="\n")  # noqa: T201


def _parse_lines(lines: Iterable[bytes | str]) -> list[GitlabIssue]:
    return list(filter(None, (parse_issue(line) for line in lines)))


def parse_issue(line: str | bytes) -> GitlabIssue | None:
    try:
        issue = cast("TypoIssue", json.loads(line))
    except json.JSONDecodeError:
        return None

    if issue.get("type", None) != "typo":
        return None

    typo = issue["typo"]
    corrections = issue["corrections"]
    path = issue["path"]
    line_num = issue.get("line_num", 1)
    description = f"typo: `{typo}` should be {', '.join(f'`{c}`' for c in corrections)}"

    return GitlabIssue(
        description=description,
        check_name="typos",
        fingerprint=_make_fingerprint(issue),
        severity="minor",
        location={"path": path, "lines": {"begin": line_num}},
    )


def _make_fingerprint(issue: TypoIssue) -> str:
    path = issue["path"]
    byte_offset = issue["byte_offset"]
    typo = issue["typo"]

    fingerprint_text = f"typos::{path}::{byte_offset}::{typo}"

    return hashlib.md5(
        fingerprint_text.encode("utf-8"),
        usedforsecurity=False,
    ).hexdigest()


if __name__ == "__main__":
    main()
