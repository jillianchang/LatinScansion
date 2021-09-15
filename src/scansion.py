"""Scansion engine."""

import functools
import logging

from typing import Iterable, List, Optional, Tuple

import pynini
from pynini.lib import rewrite

import scansion_pb2  # type: ignore


def scan_line(
    normalize_rule: pynini.Fst,
    pronounce_rule: pynini.Fst,
    variable_rule: pynini.Fst,
    syllable_rule: pynini.Fst,
    weight_rule: pynini.Fst,
    foot_rule: pynini.Fst,
    hexameter_rule: pynini.Fst,
    text: str,
    line_number: int = 0,
) -> scansion_pb2.Line:
    """Scans a single line of poetry.

    Args:
      normalize_rule: the normalization rule.
      pronounce_rule: the pronunciation rule.
      variable_rule: the rule for introducing pronunciation variation.
      syllable_rule: the syllabification rule.
      weight_rule: the weight rule.
      foot_rule: the foot rule.
      hexameter_rule: the hexameter rule.
      text: the input text.
      line_number: an optional line number (defaulting to -1).

    Returns:
      A populated Line message.
    """
    line = scansion_pb2.Line(line_number=line_number, text=text)
    # TODO: this is ugly but can be substantially redone, eventually.
    try:
        # We need escapes for normalization since Pharr uses [ and ].
        line.norm = rewrite.top_rewrite(
            pynini.escape(line.text), normalize_rule
        )
    except rewrite.Error:
        logging.error("Rewrite failure (line %d)", line.line_number)
        return line
    # Computes variant pronunciation candidates.
    pronounce_lattice = line.norm @ pronounce_rule @ variable_rule
    pronounce_lattice.project("output")
    # Filters with meter information.
    meter_lattice = (
        pronounce_lattice
        @ syllable_rule
        @ weight_rule
        @ foot_rule
        @ hexameter_rule
    )
    # Bails out if no hexameter parse is found.
    if meter_lattice.start() == pynini.NO_STATE_ID:
        line.defective = True
        logging.warning(
            "Defective line (line %d): %r", line.line_number, line.norm
        )
        return line
    line.pron = pynini.shortestpath(meter_lattice).project("input").string()
    return line


def scan_document(
    normalize_rule: pynini.Fst,
    pronounce_rule: pynini.Fst,
    variable_rule: pynini.Fst,
    syllable_rule: pynini.Fst,
    weight_rule: pynini.Fst,
    foot_rule: pynini.Fst,
    hexameter_rule: pynini.Fst,
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
        scan_line,
        normalize_rule,
        pronounce_rule,
        variable_rule,
        syllable_rule,
        weight_rule,
        foot_rule,
        hexameter_rule,
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
