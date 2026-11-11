#!/usr/bin/env python3
"""Milestone 3: Milestone 1 Task 7 with the SoupReplacer transformer API.

Task 7 sets the ``class`` attribute of every <p> tag to ``test`` and writes
the modified document. Milestone 1 did this after parsing, by looping over
``soup.find_all("p")``. Here an ``attrs_xformer`` does it while the document
is parsed, so no second pass over the tree is needed.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup, SoupReplacer
from bs4.element import Tag
from bs4.exceptions import FeatureNotFound

PARSERS = ("html.parser", "xml", "lxml", "lxml-xml")


def p_class_to_test(tag: Tag) -> dict:
    """attrs_xformer: give every <p> tag class="test"; leave others alone."""
    if tag.name != "p":
        return tag.attrs
    new_attrs = dict(tag.attrs)
    new_attrs["class"] = "test"
    return new_attrs


def choose_parser(path: Path, requested: Optional[str]) -> str:
    if requested:
        return requested
    return "xml" if path.suffix.lower() == ".xml" else "html.parser"


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Set class="test" on every <p> tag while BeautifulSoup parses the input.'
    )
    parser.add_argument("file", type=Path, help="input HTML or XML file")
    parser.add_argument(
        "-o", "--output", type=Path, default=None,
        help="output path (default: <input-stem>_task7.<suffix>)",
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
        f"{input_path.stem}_task7{input_path.suffix or '.html'}"
    )
    if output_path.resolve() == input_path.resolve():
        print("Error: output path must not overwrite the input file.", file=sys.stderr)
        return 2

    parser_name = choose_parser(input_path, args.parser)
    replacer = SoupReplacer(attrs_xformer=p_class_to_test)
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

    paragraphs = soup.find_all("p")
    # HTML parsers store class as a list (["test"]); XML keeps it a string.
    changed = sum(1 for p in paragraphs if p.get("class") in (["test"], "test"))
    print(f'Set class="test" on <p> tags during parsing. Output: {output_path}')
    print(f"<p> tags: {len(paragraphs)}; with class=\"test\": {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
