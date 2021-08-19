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

    # Tests for Aeneid Book 1, for which the combined grammar fails to scan.

    def test_aen_1_247(self):
        text = "Hīc tamen ille urbem Patavī sēdēsque locāvit"
        line = self.scan_line(text)
        self.assertEqual(
            line.pron, "hiːk tame nillurbẽː patawiː seːdeːskwe lokaːwit"
        )

    def test_aen_1_254(self):
        # MCL
        text = "Ollī subrīdēns hominum sator atque deōrum"
        line = self.scan_line(text)
        self.assertEqual(
            line.pron, "olliː subriːdeːns hominũː sato ratkwe deoːrũː"
        )

    def test_aen_1_450(self):
        text = "Hōc prīmum in lūcō nova rēs oblāta timōrem"
        line = self.scan_line(text)
        self.assertEqual(
            line.pron, "hoːk priːmin luːkoː nowa reːs oblaːta timoːrẽː"
        )

    def test_aen_1_477(self):
        text = "lōra tenēns tamen; huic cervīxque comaeque trahuntur"
        line = self.scan_line(text)
        self.assertEqual(
            line.pron, "loːra teneːns tame nujk kerwiːkskwe komajkwe trahuntur"
        )

    def test_aen_1_593(self):
        text = "argentum Pariusve lapis circumdatur aurō."
        line = self.scan_line(text)
        self.assertEqual(
            line.pron, "argentũː pariuswe lapis kirkumdatu rawroː"
        )

    def test_aen_1_649(self):
        text = "et circumtextum croceō vēlāmen acanthō,"
        line = self.scan_line(text)
        self.assertEqual(
            line.pron, "et kirkumtekstũː krokeoː weːlaːme nakantoː"
        )

    def test_aen_1_682(self):
        text = "nē quā scīre dolōs mediusve occurrere possit."
        line = self.scan_line(text)
        self.assertEqual(
            line.pron, "neː kwaː skiːre doloːs mediuswokkurrere possit"
        )

    def test_aen_1_697(self):
        text = "pallamque et pictum croceō vēlāmen acanthō."
        line = self.scan_line(text)
        self.assertEqual(
            line.pron, "pallãːkwet piktũː krokeoː weːlaːme nakantoː"
        )

    # Tests for Aeneid Book 2, for which the combined grammar fails to scan.

    def test_aen_2_202(self):
        # No poetic license rules.
        text = "Lāocoön, ductus Neptūnō sorte sacerdōs,"
        line = self.scan_line(text)
        self.assertEqual(
            line.pron, "laːokoon duktus neptuːnoː sorte sakerdoːs"
        )

    @unittest.skip("Currently failing")
    def test_aen_2_219(self):
        # Elision.
        text = "bis medium amplexī, bis collō squāmea circum"
        line = self.scan_line(text)
        self.assertEqual(
            line.pron, "bis mediãːpleksiː bis kolloː skwaːmea kircũː"
        )

    @unittest.skip("Currently failing")
    def test_aen_2_278(self):
        # Elision.
        text = "squālentem barbam et concrētōs sanguine crīnīs"
        line = self.scan_line(text)
        self.assertEqual(
            line.pron, "skwaːlentẽː barbet konkreːtoːs saŋgwine kriːniːs"
        )

if __name__ == "__main__":
    # Disables logging during testing.
    logging.disable("CRITICAL")
    unittest.main()
