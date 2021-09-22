"""Scansion engine."""

import functools
import logging

from typing import Iterable, List, Optional, Tuple

import pynini
from pynini.lib import rewrite

import scansion_pb2  # type: ignore


def scan_verse(
    normalize_rule: pynini.Fst,
    pronounce_rule: pynini.Fst,
    variable_rule: pynini.Fst,
    syllable_rule: pynini.Fst,
    weight_rule: pynini.Fst,
    foot_rule: pynini.Fst,
    hexameter_rule: pynini.Fst,
    text: str,
    verse_number: int = 0,
) -> scansion_pb2.Verse:
    """Scans a single verse of poetry.

    Args:
      normalize_rule: the normalization rule.
      pronounce_rule: the pronunciation rule.
      variable_rule: the rule for introducing pronunciation variation.
      syllable_rule: the syllabification rule.
      weight_rule: the weight rule.
      foot_rule: the foot rule.
      hexameter_rule: the hexameter rule.
      text: the input text.
      verse_number: an optional verse number (defaulting to -1).

    Returns:
      A populated Verse message.
    """
    verse = scansion_pb2.Verse(verse_number=verse_number, text=text)
    # TODO: this is ugly but can be substantially redone, eventually.
    try:
        # We need escapes for normalization since Pharr uses [ and ].
        verse.norm = rewrite.top_rewrite(
            pynini.escape(verse.text), normalize_rule
        )
    except rewrite.Error:
        logging.error("Rewrite failure (verse %d)", verse.verse_number)
        return verse
    try:
        verse.raw_pron = rewrite.top_rewrite(verse.norm, pronounce_rule)
    except rewrite.Error:
        logging.error("Rewrite failure (verse %d)", verse.verse_number)
        return verse
    # Computes variant pronunciation candidates.
    try:
        pron_lattice = rewrite.rewrite_lattice(verse.raw_pron, variable_rule)
    except rewrite.Error:
        logging.error("Rewrite failure (verse %d)", verse.verse_number)
        return verse
    # Filters with meter information.
    pron_lattice @= syllable_rule
    pron_lattice @= weight_rule
    pron_lattice @= foot_rule
    pron_lattice @= hexameter_rule
    # Bails out if no hexameter parse is found.
    if pron_lattice.start() == pynini.NO_STATE_ID:
        verse.defective = True
        logging.warning(
            "Defective verse (verse %d): %r", verse.verse_number, verse.norm
        )
        return verse
    verse.var_pron = (
        pynini.shortestpath(pron_lattice).project("input").string()
    )
    return verse


def scan_document(
    normalize_rule: pynini.Fst,
    pronounce_rule: pynini.Fst,
    variable_rule: pynini.Fst,
    syllable_rule: pynini.Fst,
    weight_rule: pynini.Fst,
    foot_rule: pynini.Fst,
    hexameter_rule: pynini.Fst,
    verses: Iterable[str],
    name: Optional[str] = None,
) -> scansion_pb2.Document:
    """Scans an entire document.

    Args:
      normalize_rule: the normalization rule.
      pronounce_rule: the pronunciation rule.
      variable_rule: the rule for introducing pronunciation variation.
      meter_rule: the rule for constraining pronunciation variation to scan.
      verses: an iterable of verses to scan.
      name: optional metadata about the source.

    Returns:
      A populated Document message.
    """
    document = scansion_pb2.Document(name=name)
    # This binds the rule nmes ahead of time.
    curried = functools.partial(
        scan_verse,
        normalize_rule,
        pronounce_rule,
        variable_rule,
        syllable_rule,
        weight_rule,
        foot_rule,
        hexameter_rule,
    )
    scanned_verses = 0
    defective_verses = 0
    for verse_number, verse in enumerate(verses, 1):
        # TODO(kbg): the `append` method copies the message to avoid circular
        # references. Would we improve performance using the `add` method and
        # passing the empty message to be mutated?
        scanned = curried(verse, verse_number)
        document.verse.append(scanned)
        if scanned.defective:
            defective_verses += 1
        else:
            scanned_verses += 1
    logging.info("%d verses scanned", scanned_verses)
    logging.info("%d verses defective", defective_verses)
    return document
