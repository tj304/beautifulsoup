#!/usr/bin/env python3
"""Milestone 2, Part 3: replace <b> tags during parsing with SoupReplacer."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup, SoupReplacer
from bs4.exceptions import FeatureNotFound

PARSERS = ("html.parser", "xml", "lxml", "lxml-xml")


def choose_parser(path: Path, requested: Optional[str]) -> str:
    if requested:
        return requested
    return "xml" if path.suffix.lower() == ".xml" else "html.parser"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replace <b> tags with <blockquote> while BeautifulSoup parses the input."
    )
    parser.add_argument("file", type=Path, help="input HTML or XML file")
    parser.add_argument(
        "-o", "--output", type=Path, default=None,
        help="output path (default: <input-stem>_replaced.<suffix>)",
    )
    parser.add_argument(
        "--parser", choices=PARSERS, default=None,
        help="parser to use (default: xml for .xml files, otherwise html.parser)",
    )
    args = parser.parse_args()

    input_path: Path = args.file
    if not input_path.is_file():
        print(f"Error: input file does not exist: {input_path}", file=sys.stderr)
        return 2

    output_path: Path = args.output or input_path.with_name(
        f"{input_path.stem}_replaced{input_path.suffix or '.html'}"
    )
    if output_path.resolve() == input_path.resolve():
        print("Error: output path must not overwrite the input file.", file=sys.stderr)
        return 2

    parser_name = choose_parser(input_path, args.parser)
    replacer = SoupReplacer("b", "blockquote")
    try:
        with input_path.open("rb") as source:
            soup = BeautifulSoup(source, parser_name, replacer=replacer)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(soup.prettify(), encoding="utf-8")
    except FeatureNotFound as exc:
        print(
            f"Error: parser {parser_name!r} is unavailable. For XML or lxml parsing, "
            "install the optional dependency with 'python -m pip install lxml'.\n"
            f"Details: {exc}",
            file=sys.stderr,
        )
        return 2
    except OSError as exc:
        print(f"Error processing the input or output file: {exc}", file=sys.stderr)
        return 2

    print(f"Replaced <b> tags with <blockquote> during parsing. Output: {output_path}")
    print(f"Remaining <b> tags: {len(soup.find_all('b'))}")
    print(f"Replacement <blockquote> tags: {len(soup.find_all('blockquote'))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
