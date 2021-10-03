"""Scansion engine."""

import functools
import logging

from typing import Iterable, List, Optional, Tuple

import pynini
from pynini.lib import rewrite

import scansion_pb2  # type: ignore


def _chunk(fst: pynini.Fst) -> List[Tuple[str, str]]:
    """Chunks a string transducer into tuples.

    This function is given a string transducer of the form:

        il1 il2 il3 il4 il5 il6
        ol1 eps eps ol2 eps ol3

    And returns the list:

        [(il1 il2 il3, ol1), (il4 il5, ol2), (il6, ol3)]

    It thus recovers the "many-to-one" alignment.

    Args:
      fst: a string transducer containing the alignment.

    Returns:
      A list of string, char tuples.
    """
    # Input epsilon-normalization and removal forces a sensible alignment.
    fst = pynini.epsnormalize(fst).rmepsilon()
    assert (
        fst.properties(pynini.STRING, True) == pynini.STRING
    ), "FST is not a string automaton"
    alignment: List[Tuple[str, str]] = []
    state = 0
    arc = fst.arcs(state).value()
    assert arc.ilabel, f"Input label leaving state {state} contains epsilon"
    ilabels = bytearray([arc.ilabel])
    assert arc.olabel, f"Output label leaving state {state} contains epsilon"
    olabel = arc.olabel
    for state in range(1, fst.num_states() - 1):
        arc = fst.arcs(state).value()
        assert (
            arc.ilabel
        ), f"Input label leaving state {state} contains epsilon"
        # A non-epsilon olabel signals a new chunk.
        if arc.olabel:
            alignment.append((ilabels.decode("utf8"), chr(olabel)))
            ilabels.clear()
            olabel = arc.olabel
        ilabels.append(arc.ilabel)
    assert (
        ilabels
    ), f"Input label leaving penultimate state {state}  contains epsilon"
    alignment.append((ilabels.decode("utf8"), chr(olabel)))
    return alignment


def scan_verse(
    normalize_rule: pynini.Fst,
    pronounce_rule: pynini.Fst,
    variable_rule: pynini.Fst,
    syllable_rule: pynini.Fst,
    weight_rule: pynini.Fst,
    hexameter_rule: pynini.Fst,
    text: str,
    number: int = 0,
) -> scansion_pb2.Verse:
    """Scans a single verse of poetry.

    Args:
      normalize_rule: the normalization rule.
      pronounce_rule: the pronunciation rule.
      variable_rule: the rule for introducing pronunciation variation.
      syllable_rule: the syllabification rule.
      weight_rule: the weight rule.
      hexameter_rule: the hexameter rule.
      text: the input text.
      number: an optional verse number (defaulting to -1).

    Returns:
      A populated Verse message.
    """
    verse = scansion_pb2.Verse(number=number, text=text)
    try:
        verse.norm = rewrite.top_rewrite(
            # We need escapes for normalization since Pharr uses [ and ].
            pynini.escape(verse.text),
            normalize_rule,
        )
    except rewrite.Error:
        logging.error("Rewrite failure (verse %d)", verse.number)
        return verse
    try:
        verse.raw_pron = rewrite.top_rewrite(verse.norm, pronounce_rule)
    except rewrite.Error:
        logging.error("Rewrite failure (verse %d)", verse.number)
        return verse
    var = verse.raw_pron @ variable_rule
    syllable = pynini.project(var, "output") @ syllable_rule
    weight = pynini.project(syllable, "output") @ weight_rule
    foot = pynini.project(weight, "output") @ hexameter_rule
    if foot.start() == pynini.NO_STATE_ID:
        verse.defective = True
        logging.warning(
            "Defective verse (verse %d): %r", verse.number, verse.norm
        )
        return verse
    # Works backwards to obtain intermediate structure.
    foot = pynini.arcmap(pynini.shortestpath(foot), map_type="rmweight")
    weight = pynini.shortestpath(weight @ pynini.project(foot, "input"))
    syllable = pynini.shortestpath(syllable @ pynini.project(weight, "input"))
    # Writes structure to message.
    verse.var_pron = pynini.project(syllable, "input").string()
    foot_chunks = _chunk(foot)
    weight_chunks = _chunk(weight)
    syllable_chunks = _chunk(syllable)
    # These help us preserve the multi-alignment.
    weight_chunk_idx = 0
    syllable_chunk_idx = 0
    for weight_codes, foot_code in foot_chunks:
        # The foot type enum uses the ASCII decimals; see scansion.proto.
        foot = verse.foot.add(type=ord(foot_code))
        for weight_code in weight_codes:
            syllable_codes, exp_weight_code = weight_chunks[weight_chunk_idx]
            assert (
                weight_code == exp_weight_code
            ), f"Weight code mismatch: {weight_code!r} != {exp_weight_code!r}"
            weight_chunk_idx += 1
            # Skips over whitespace between words.
            if weight_code.isspace():
                # We also advance one step in the syllable chunking or this
                # will become misaligned.
                syllable_chunk_idx += 1
                continue
            syllable = foot.syllable.add(weight=ord(weight_code))
            for syllable_code in syllable_codes:
                var_codes, exp_syllable_code = syllable_chunks[
                    syllable_chunk_idx
                ]
                assert syllable_code == exp_syllable_code, (
                    "Syllable code mismatch: "
                    f"{syllable_code!r} != {exp_syllable_code!r}"
                )
                syllable_chunk_idx += 1
                # Skips over whitespace between words.
                if syllable_code.isspace():
                    continue
                if syllable_code == "O":
                    syllable.onset = var_codes
                elif syllable_code in ("-", "U"):
                    syllable.nucleus = var_codes
                elif syllable_code == "C":
                    syllable.coda = var_codes
                else:
                    raise AssertionError(
                        f"Unknown syllable code: {syllable_code}"
                    )
    return verse


def scan_document(
    normalize_rule: pynini.Fst,
    pronounce_rule: pynini.Fst,
    variable_rule: pynini.Fst,
    syllable_rule: pynini.Fst,
    weight_rule: pynini.Fst,
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
        hexameter_rule,
    )
    scanned_verses = 0
    defective_verses = 0
    for number, verse in enumerate(verses, 1):
        # TODO(kbg): the `append` method copies the message to avoid circular
        # references. Would we improve performance using the `add` method and
        # passing the empty message to be mutated?
        scanned = curried(verse, number)
        document.verse.append(scanned)
        if scanned.defective:
            defective_verses += 1
        else:
            scanned_verses += 1
    logging.info("%d verses scanned", scanned_verses)
    logging.info("%d verses defective", defective_verses)
    return document
