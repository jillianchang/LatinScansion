#!/usr/bin/env python
"""Rewrites the contents of a text file, line by line, using FST grammar rules.

The user provides the path of the input file, the path to an OpenFst FAR file,
and a list of rules to apply; the result is printed to standard output.

In the case that multiple rewrites are available, just one top rewrite is
printed. Tie resolution is implementation-defined unless --one-top-rewrite is
enabled, in which case the presence of ties results in a fatal error.
"""

import argparse
import fileinput
import functools
import logging

from typing import Callable, Union

import pynini
from pynini.lib import rule_cascade


def _prepare_token_type(
    token_type: str,
) -> Union[str, pynini.SymbolTable]:
    """Passes through standard token types and loads a symbol table."""
    if token_type in ["byte", "utf8"]:
        return token_type
    else:
        return pynini.SymbolTable.read_text(token_type)


def main(args: argparse.Namespace) -> None:
    cascade = rule_cascade.RuleCascade(args.far)
    cascade.set_rules(args.rules)
    rewrite: Callable[[str], str] = functools.partial(
        cascade.one_top_rewrite
        if args.one_top_rewrite
        else cascade.top_rewrite,
        input_token_type=_prepare_token_type(args.input_token_type),
        output_token_type=_prepare_token_type(args.output_token_type),
    )
    for line in fileinput.input(args.input):
        line = line.rstrip()
        # If we're using a string-based input token type, we want to escape
        # specialized tokens.
        if args.input_token_type in ["byte", "utf8"]:
            line = pynini.escape(line)
        try:
            print(rewrite(line))
        except Exception as err:
            logging.error(
                "Exception at %s (line %d): %s (%r)",
                fileinput.filename(),
                fileinput.lineno(),
                err,
                line,
            )
            exit(1)


if __name__ == "__main__":
    logging.basicConfig(level="INFO", format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", default="-", help="path to input file (default: stdin)"
    )
    parser.add_argument("--far", required=True, help="path to input FAR file")
    parser.add_argument(
        "--rules",
        required=True,
        nargs="+",
        help="list of one or more FAR rules to apply",
    )
    parser.add_argument(
        "--input-token-type",
        default="byte",
        help="input token type (default: %(default)s), "
        "or path to symbol table",
    )
    parser.add_argument(
        "--output-token-type",
        default="byte",
        help="output token type (default: %(default)s), "
        "or path to symbol table",
    )
    parser.add_argument(
        "--one-top-rewrite",
        action="store_true",
        help="makes the presence of ties produce a fatal error",
    )
    main(parser.parse_args())
