from __future__ import annotations

from typos_gitlab_code_quality import parse_issue


def test_parse_issue() -> None:
    issue = parse_issue(
        '{"type":"typo","path":"./module.py","line_num":4,"byte_offset":15,"typo":"issu","corrections":["issue"]}',
    )

    assert issue == {
        "description": "typo: `issu` should be `issue`",
        "check_name": "typos",
        "severity": "minor",
        "fingerprint": "bfc9c7c1f298b8beab529ec0a695d756",
        "location": {"path": "./module.py", "lines": {"begin": 4}},
    }


def test_parse_issue_ignore_non_json() -> None:
    assert parse_issue("unknown") is None


def test_parse_issue_ignore_non_typo() -> None:
    assert parse_issue('{"type":"unknown"}') is None
