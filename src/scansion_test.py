"""Unit tests for scansion.py."""

import functools
import logging
import unittest

import pynini

import scansion


class ScansionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with pynini.Far("../grammars/all.far", "r") as far:
            cls.scan_line = functools.partial(
                scansion.scan_line,
                far["NORMALIZE"],
                far["PRONOUNCE"],
                far["VARIABLE"],
                far["METER"],
            )

    # TODO(jillianchang): There should be way more tests than this.

    def test_aen_1_1(self):
        # Scans line 1.1.
        text = "Arma virumque canō, Trojae quī prīmus ab ōris"
        line = self.scan_line(text)  # No explicit line number.
        self.assertEqual(line.line_number, -1)
        self.assertEqual(line.text, text)
        self.assertEqual(
            line.norm, "arma virumque canō trojae quī prīmus ab ōris"
        )
        self.assertEqual(
            line.pron, "arma wirũːkwe kanoː trojjaj kwiː priːmu sa boːris"
        )

    def test_aen_1_534(self):
        # Scans line 1.534, which is clearly defective (and in this case, it's
        # entirely possible Virgil never finished it).
        text = "Hic cursus fuit,"
        line = self.scan_line(text, 534)
        self.assertEqual(line.line_number, 534)
        self.assertEqual(line.text, text)
        self.assertEqual(line.norm, "hic cursus fuit")
        self.assertTrue(line.defective)

    def test_aen_2_77(self):
        # Scans line 2.77, which has brackets in Pharr's edition.
        text = "[Ille haec dēpositā tandem formīdine fātur:]"
        line = self.scan_line(text, 77)
        self.assertEqual(line.line_number, 77)
        self.assertEqual(line.text, text)
        self.assertEqual(
            line.norm, "ille haec dēpositā tandem formīdine fātur"
        )
        self.assertFalse(line.defective)


if __name__ == "__main__":
    # Disables logging during testing.
    logging.disable("CRITICAL")
    unittest.main()
