"""Milestone 2, Part 1, Task 3: try SoupStrainer while listing every tag."""

import argparse
import sys
from pathlib import Path
from time import perf_counter
from typing import Optional

from bs4 import BeautifulSoup, SoupStrainer
from bs4.exceptions import FeatureNotFound


PARSERS = ("html.parser", "xml", "lxml", "lxml-xml")


def choose_parser(path: Path, requested: Optional[str]) -> str:
    """Use an explicitly selected parser, or infer XML from the extension."""
    if requested:
        return requested
    return "xml" if path.suffix.lower() == ".xml" else "html.parser"


def main() -> int:
    arg_parser = argparse.ArgumentParser(
        description="List every tag while passing an unrestricted SoupStrainer."
    )
    arg_parser.add_argument("file", type=Path, help="input HTML or XML file")
    arg_parser.add_argument(
        "--parser",
        choices=PARSERS,
        default=None,
        help="parser to use (default: xml for .xml files, otherwise html.parser)",
    )
    args = arg_parser.parse_args()

    input_path: Path = args.file
    if not input_path.is_file():
        print(f"Error: input file does not exist: {input_path}", file=sys.stderr)
        return 2

    parser_name = choose_parser(input_path, args.parser)
    start = perf_counter()
    try:
        with input_path.open("rb") as source:
            # An empty SoupStrainer has no tag-name or attribute restrictions.
            # This deliberately attempts the requested API, but retains all tags
            # and therefore is not expected to save much parsing time or memory.
            soup = BeautifulSoup(
                source,
                parser_name,
                parse_only=SoupStrainer(),
            )
    except FeatureNotFound as exc:
        print(
            f"Error: parser {parser_name!r} is unavailable. "
            "For XML or lxml parsing, install the optional dependency with "
            "'python -m pip install lxml'.\n"
            f"Details: {exc}",
            file=sys.stderr,
        )
        return 2
    except OSError as exc:
        print(f"Error reading {input_path}: {exc}", file=sys.stderr)
        return 2
    parse_seconds = perf_counter() - start

    tags = soup.find_all(True)
    print(f"Found {len(tags)} tag(s) in {input_path}:")
    for index, tag in enumerate(tags, start=1):
        # Print each tag's name and attributes so nested markup is not repeatedly
        # printed as part of every ancestor's serialized HTML.
        print(f"{index}. <{tag.name}> attrs={tag.attrs}")

    print(
        f"[info] parser={parser_name}; input_bytes={input_path.stat().st_size}; "
        f"parse_seconds={parse_seconds:.3f}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
