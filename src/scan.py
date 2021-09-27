#!/usr/bin/env python
"""Command-line scansion driver."""

import argparse
import contextlib
import logging
import os.path

from google.protobuf import text_format  # type: ignore
import pynini

import scansion


def main(args: argparse.Namespace) -> None:
    with contextlib.ExitStack() as stack:
        far = stack.enter_context(pynini.Far(args.far, "r"))
        source = stack.enter_context(open(args.input, "r"))
        sink = stack.enter_context(open(args.output, "w"))
        lines = [line.rstrip() for line in source]
        document = scansion.scan_document(
            far["NORMALIZE"],
            far["PRONOUNCE"],
            far["VARIABLE"],
            far["SYLLABLE"],
            far["WEIGHT"],
            far["HEXAMETER"],
            lines,
            args.name if args.name else os.path.normpath(args.input),
        )
        text_format.PrintMessage(document, sink, as_utf8=True)


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s", level="INFO")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="path for input text document")
    parser.add_argument("output", help="path for output textproto document")
    parser.add_argument("--far", required=True, help="path to grammar FAR")
    parser.add_argument("--name", help="optional name field")
    main(parser.parse_args())
