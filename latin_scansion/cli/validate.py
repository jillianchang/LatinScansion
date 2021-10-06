"""Validates Document textprotos."""

import argparse
import logging

import latin_scansion


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "textproto", nargs="+", help="path for input textproto"
    )
    parser.add_argument(
        "--canonicalize",
        action="store_true",
        help="canonicalize input textprotos upon successful parse?",
    )
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(format="%(levelname)s: %(message)s", level="INFO")
    args = _parse_args()
    for textproto in args.textproto:
        try:
            document = latin_scansion.read_document(textproto)
            logging.info("Successfully validated %s", textproto)
            if args.canonicalize:
                logging.info("Canonicalizing contents of %s", textproto)
                latin_scansion.write_document(document, textproto)
        # TODO(kbg): Can I make this more explicit?
        except Exception as err:
            logging.info("Validation of %s failed: %s", textproto, err)
