"""Scansion engine."""

import functools
import logging

from typing import Iterable, List, Optional, Tuple

import pynini
from pynini.lib import rewrite

import scansion_pb2  # type: ignore


def _forward(fst1: pynini.FstLike, fst2: pynini.FstLike) -> pynini.Fst:
    # TODO: docs?
    return fst1 @ pynini.project(fst2, "input")


def _backward(fst1: pynini.FstLike, fst2: pynini.FstLike) -> pynini.Fst:
    # TODO: docs?
    return pynini.shortestpath(pynini.project(fst1, "output") @ fst2)


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
    var_lattice = _forward(verse.raw_pron, variable_rule)
    syllable_lattice = _forward(var_lattice, syllable_rule)
    weight_lattice = _forward(syllable_lattice, weight_rule)
    foot_lattice = _forward(weight_lattice, foot_rule)
    # Filters out any non-hexameter parses.
    foot_lattice @= hexameter_rule
    if foot_lattice.start() == pynini.NO_STATE_ID:
        verse.defective = True
        logging.warning(
            "Defective verse (verse %d): %r", verse.verse_number, verse.norm
        )
        return verse
    # Work backwards to obtain intermediate structure.
    weight_lattice = _backward(weight_lattice, foot_lattice)
    syllable_lattice = _backward(syllable_lattice, weight_lattice)
    var_lattice = _backward(var_lattice, syllable_lattice)
    """
    verse.var_pron = pynini.shortestpath(var_lattice).string()
    # Encodes variable structure.
    verse.var_pron = var_lattice.string()
    # TODO: Encodes feet structure.
    paths = weight_lattice.paths()
    print(zip(paths.ilabels(), paths.olabels()))
    foot_lattice = pynini.shortestpath(foot_lattice)
    for foot_code in foot_lattice.string():
        foot = verse.foot.add()
        foot.type = ord(foot_code)
    """
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
