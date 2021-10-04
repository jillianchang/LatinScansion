"""Validates Document textprotos."""

import argparse
import logging


from latin_scansion import textproto


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
    for path in args.textproto:
        try:
            document = textproto.read_document(path)
            logging.info("Successfully validated %s", path)
            if args.canonicalize:
                logging.info("Canonicalizing contents of %s", path)
                textproto.write_document(document, path)
        # TODO(kbg): Can I make this more explicit?
        except Exception as err:
            logging.info("Validation of %s failed: %s", path, err)
