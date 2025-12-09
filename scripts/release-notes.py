# /// script
# dependencies = []
# ///
# pyright: reportUnusedCallResult=false
# ruff: noqa: ERA001
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import textwrap
from itertools import dropwhile, takewhile
from pathlib import Path
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from collections.abc import Sequence


def main(args: Sequence[str] | None = None) -> None:
    """Command line entry point."""
    parser = argparse.ArgumentParser(
        description="Generate release notes from changelog file",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--changelog",
        default="CHANGELOG.md",
        help="Changelog file",
        type=Path,
    )
    parser.add_argument(
        "--version",
        required=True,
        help="Version section in the changelog file",
    )
    # parser.add_argument(
    #     "--capture-start",
    #     default=r"^## \[{version}\]",
    #     help="The capture start when this regex pattern match a line in `--changelog`"
    # )
    # parser.add_argument(
    #     "--capture-end",
    #     default=r"^## ",
    #     help=textwrap.dedent("""
    #     The capture end when this regex pattern match a line in `--changelog`,
    #     or when end of file is reached
    #     """)
    # )
    parser.add_argument(
        "--diff-url",
        required=False,
        help=textwrap.dedent("""\
        Optional url format string for comparing between 2 tags.
        It should contain a '{old}' and '{new}' placeholders
        that will be filled by the `previous tag` (old) and `version` (new).
        The `old` tag is the closest reachable tag from the `version` tag.

        - GitLab CI: "$CI_PROJECT_URL/-/compare/{old}...{new}"
        - GitHub Workflow: "$GITHUB_SERVER_URL/$GITHUB_REPOSITORY/compare/{old}...{new}"
        """),
    )

    namespace = parser.parse_args(args)

    changelog = cast("Path", namespace.changelog)
    if not changelog.is_file():
        raise FileNotFoundError(changelog)

    tag = cast("str", namespace.version)
    diff_url = cast("str | None", namespace.diff_url)
    text = _extract(changelog, tag)

    if diff_url:
        prev_tag = _get_previous_tag(tag)
        if prev_tag:
            url = diff_url.format(old=prev_tag, new=tag)
            text += f"\n\n**Full Changelog:** [{prev_tag}...{tag}]({url})"

    print(text, file=sys.stdout)


def _get_previous_tag(tag: str) -> str | None:
    # Gets reachable tags, ordered by creating date, starting from `tag`
    tags = subprocess.run(
        ["git", "tag", "--sort=-creatordate", "--merged", tag],
        capture_output=True,
        check=True,
    ).stdout.splitlines()

    if len(tags) > 1:
        return tags[1].decode().strip()

    return None


def _extract(changelog: Path, version: str) -> str:
    start_pattern = re.compile(rf"^## \[{re.escape(version)}\]")
    end_pattern = re.compile(r"^## ")

    lines: list[str] = []
    with changelog.open("r") as f:
        capture = dropwhile(lambda x: not start_pattern.match(x), f)

        try:
            lines.append(next(capture))
        except StopIteration:
            msg = f"No match for version `{version}`"
            raise RuntimeError(msg) from None

        lines.extend(takewhile(lambda x: not end_pattern.match(x), capture))

    # Convert to h1 by removing the first '#', e.g., `## Title` -> `# Title`
    # TODO(tga): Parse with https://github.com/lepture/mistune
    lines[0] = lines[0][1:]
    lines[1:1] = ["\n", "## Release Notes", "\n"]

    return "".join(lines).strip()


if __name__ == "__main__":
    main()
