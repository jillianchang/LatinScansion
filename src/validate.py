#!/usr/bin/env python
"""Validates Document textprotos."""

import argparse
import logging

import textproto


def main(args: argparse.Namespace) -> None:
    for path in args.textproto:
        try:
            document = textproto.read_document(path)
            logging.info("Successfully validated %s", path)
            if args.canonicalize:
                logging.info("Canonicalizing contents of %s", path)
                textproto.write_document(document, path)
        except Exception as err:
            logging.info("Validation of %s failed: %s", path, err)


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s", level="INFO")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "textproto", nargs="+", help="path for input textproto"
    )
    parser.add_argument(
        "--canonicalize",
        action="store_true",
        help="canonicalize input textprotos upon successful parse?",
    )
    main(parser.parse_args())
