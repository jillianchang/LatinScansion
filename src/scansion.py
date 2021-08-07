"""Scansion engine."""

import functools
import logging

from typing import Iterable, Optional

import pynini
from pynini.lib import rewrite

import scansion_pb2  # type: ignore


def scan_line(
    normalize_rule: pynini.Fst,
    pronounce_rule: pynini.Fst,
    variable_rule: pynini.Fst,
    meter_rule: pynini.Fst,
    text: str,
    line_number: Optional[int] = None,
) -> scansion_pb2.Line:
    """Scans a single line of poetry.

    Args:
      normalize_rule: the normalization rule.
      pronounce_rule: the pronunciation rule.
      variable_rule: the rule for introducing pronunciation variation.
      meter_rule: the rule for constraining pronunciation variation to scan.
      text: the input text.

    Returns:
      A populated Line message.
    """
    line = scansion_pb2.Line(line_number=line_number, text=text.strip())
    # Applies normalization.
    try:
        line.norm = rewrite.top_rewrite(line.text, normalize_rule)
    except rewrite.Error:
        logging.error(
            "Rewrite failure during normalization (line %d): %r",
            line_number,
            line.text,
        )
        return line
    # Applies pronunciation.
    try:
        pron_before_variable = rewrite.top_rewrite(line.norm, pronounce_rule)
        # The output tape contains possible variable pronunciations.
        lattice = rewrite.rewrite_lattice(pron_before_variable, variable_rule)
        # By intersecting the output tape with the meter rule, we eliminate
        # variable pronunciations that don't scan.
        lattice @= meter_rule
        # If no such variable pronunciations exist, we have a defective line,
        # or a deficiency in the variable rule grammar.
        if lattice.start() == pynini.NO_STATE_ID:
            line.defective = True
            logging.warning(
                "Defective line (line %d): %r", line_number, line.norm
            )
            return line
        # TODO(kbg): by grabbing the string before projecting we can also get
        # a list of the feet ('D', 'S', and 'T').
        line.pron = pynini.shortestpath(lattice).project("input").string()
    except rewrite.Error:
        logging.error("Rewrite failure during pronunciation: %r", line.norm)
    return line


def scan_document(
    normalize_rule: pynini.Fst,
    pronounce_rule: pynini.Fst,
    variable_rule: pynini.Fst,
    meter_rule: pynini.Fst,
    lines: Iterable[str],
    name: Optional[str] = None,
) -> scansion_pb2.Document:
    """Scans an entire document.

    Args:
      normalize_rule: the normalization rule.
      pronounce_rule: the pronunciation rule.
      variable_rule: the rule for introducing pronunciation variation.
      meter_rule: the rule for constraining pronunciation variation to scan.
      lines: an iterable of lines to scan.
      name: optional metadata about the source.

    Returns:
      A populated Document message.
    """
    document = scansion_pb2.Document(name=name)
    # This binds the rule nmes ahead of time.
    curried = functools.partial(
        scan_line, normalize_rule, pronounce_rule, variable_rule, meter_rule
    )
    scanned_lines = 0
    defective_lines = 0
    for line_number, line in enumerate(lines, 1):
        # TODO(kbg): the `append` method copies the message to avoid circular
        # references. Would we improve performance using the `add` method and
        # passing the empty message to be mutated?
        scanned = curried(line, line_number)
        document.line.append(scanned)
        if scanned.defective:
            defective_lines += 1
        else:
            scanned_lines += 1
    logging.info("%d lines scanned", scanned_lines)
    logging.info("%d lines defective", defective_lines)
    return document
