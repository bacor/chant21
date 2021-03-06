import unittest
from chant21.cantus import ParserCantusVolpiano
from chant21.cantus import HyphenationError
from chant21.cantus import BarlineError
from chant21.cantus import ClefError
from chant21.cantus import UnsupportedCharacterError

class TestParser(unittest.TestCase):
    def test_missing_clef(self):
        parser = ParserCantusVolpiano()
        test_fn = lambda : parser.parse('f---f')
        self.assertRaises(ClefError, test_fn)

    def test_invalid_clef_hyphenation(self):
        parser = ParserCantusVolpiano()
        test_fn = lambda : parser.parse('1-f---f')
        self.assertRaises(HyphenationError, test_fn)
        test_fn = lambda : parser.parse('1f---f')
        self.assertRaises(HyphenationError, test_fn)

    def test_mixed_hyphenation_strict(self):
        parser = ParserCantusVolpiano()
        test_fn = lambda : parser.parse('1--f---f', strict=True)
        self.assertRaises(HyphenationError, test_fn)
    
    def test_mixed_hyphenation_not_strict(self):
        parser = ParserCantusVolpiano()
        parse = parser.parse('1--f---f', strict=False)
        self.assertTrue(True)

    def test_4_5_hyphens_strict(self):
        parser = ParserCantusVolpiano()
        test_fn = lambda : parser.parse('1---f----f', strict=True)
        self.assertRaises(HyphenationError, test_fn)

        parser = ParserCantusVolpiano()
        test_fn = lambda : parser.parse('1---f-----f', strict=True)
        self.assertRaises(HyphenationError, test_fn)

    def test_4_5_hyphens_not_strict(self):
        parser = ParserCantusVolpiano()
        parse = parser.parse('1---f----f-g--g----gf', strict=False)
        self.assertTrue(True)

    def test_missing_pitches_hyphenation_strict(self):
        parser = ParserCantusVolpiano()
        test_fn = lambda : parser.parse('1---f--6------6---f', strict=True)
        self.assertRaises(HyphenationError, test_fn)
        test_fn = lambda : parser.parse('1---f---6------6--f', strict=True)
        self.assertRaises(HyphenationError, test_fn)

        test_fn = lambda : parser.parse('1---f---76------677--f', strict=True)
        self.assertRaises(HyphenationError, test_fn)
    
    def test_missing_pitches_hyphenation_not_strict(self):
        parser = ParserCantusVolpiano()
        parse = parser.parse('1---f--6------6---f--6------6---g', strict=False)
        self.assertTrue(True)
        parse = parser.parse('1---f---76------677--f', strict=False)
        self.assertTrue(True)

    def test_missing_pitches_too_many_hyphens_strict(self):
        parser = ParserCantusVolpiano()
        test_fn = lambda : parser.parse('1---f---6-------6---f', strict=True)
        self.assertRaises(HyphenationError, test_fn)

    def test_missing_pitches_too_many_hyphens_not_strict(self):
        parser = ParserCantusVolpiano()
        parser.parse('1---6-------6', strict=False)
        parser.parse('1---6-------------6---f', strict=False)
        self.assertTrue(True)
    
    def test_double_3_strict(self):
        parser = ParserCantusVolpiano()
        test_fn = lambda : parser.parse('1---f---33---g', strict=True)
        self.assertRaises(BarlineError, test_fn)

    def test_double_3_not_strict(self):
        parser = ParserCantusVolpiano()
        parse = parser.parse('1---f---33---g', strict=False)
        self.assertTrue(True)

    def test_thick_barline_strict(self):
        parser = ParserCantusVolpiano()
        test_fn = lambda : parser.parse('1---f---5', strict=True)
        self.assertRaises(BarlineError, test_fn)

    def test_thick_barline_not_strict(self):
        parser = ParserCantusVolpiano()
        parse = parser.parse('1---f---5', strict=False)
        self.assertTrue(True)

    def test_too_few_hyphens_before_barline_strict(self):
        parser = ParserCantusVolpiano()
        test_fn = lambda : parser.parse('1---f-3', strict=True)
        self.assertRaises(HyphenationError, test_fn)
        test_fn = lambda : parser.parse('1---f--3', strict=True)
        self.assertRaises(HyphenationError, test_fn)
        test_fn = lambda : parser.parse('1---f--4', strict=True)
        self.assertRaises(HyphenationError, test_fn)

    def test_too_few_hyphens_before_barline_not_strict(self):
        parser = ParserCantusVolpiano()
        parser.parse('1---f-3', strict=False)
        parser.parse('1---f--3', strict=False)
        parser.parse('1---f-4', strict=False)
        parser.parse('1---f--4', strict=False)
        self.assertTrue(True)

    def test_too_few_hyphens_after_barline_strict(self):
        parser = ParserCantusVolpiano()
        test_fn = lambda : parser.parse('1---f---3-f', strict=True)
        self.assertRaises(HyphenationError, test_fn)
        test_fn = lambda : parser.parse('1---f---3--f', strict=True)
        self.assertRaises(HyphenationError, test_fn)
        test_fn = lambda : parser.parse('1---f---4--f', strict=True)
        self.assertRaises(HyphenationError, test_fn)

    def test_too_few_hyphens_after_barline_not_strict(self):
        parser = ParserCantusVolpiano()
        parser.parse('1---f---3-f', strict=False)
        parser.parse('1---f---3--f', strict=False)
        parser.parse('1---f---4-f', strict=False)
        parser.parse('1---f---4--f', strict=False)
        self.assertTrue(True)

    def test_dot_strict(self):
        parser = ParserCantusVolpiano()
        test_fn = lambda : parser.parse('1---fg.', strict=True)
        self.assertRaises(UnsupportedCharacterError, test_fn)

    def test_dot_not_strict(self):
        parser = ParserCantusVolpiano()
        parser.parse('1---fg.', strict=False)
        self.assertTrue(True)

    def test_alternative_hyphenation_strict(self):
        parser = ParserCantusVolpiano()
        test_fn = lambda : parser.parse('1--fg-f--g', strict=True)
        self.assertRaises(HyphenationError, test_fn)

    def test_alternative_hyphenation_not_strict(self):
        parser = ParserCantusVolpiano()
        parse = parser.parse('1--fg-f-f--g', strict=False)
        vol = parse.value.replace(' ', '').replace('|', '')
        self.assertEqual(vol, '1---fg--f--f---g')

class TestSyllable(unittest.TestCase):
    """Tests using `syllable` as the root node"""

    def test_syllables(self):
        parser = ParserCantusVolpiano(root='syllable')
        parse = parser.parser.parse('fgf-ef')
        self.assertEqual(len(parse), 3)
        self.assertEqual(parse[0].rule_name, 'neume')
        self.assertEqual(parse[1].rule_name, 'neume_boundary')
        self.assertEqual(parse[2].rule_name, 'neume')
    
    def test_other(self):
        parser = ParserCantusVolpiano(root='syllable')
        parse = parser.parser.parse('3')
        self.assertEqual(len(parse), 1)
        self.assertEqual(parse[0].rule_name, 'section_end')

        parse = parser.parser.parse('4')
        self.assertEqual(len(parse), 1)
        self.assertEqual(parse[0].rule_name, 'chant_end')

        parse = parser.parser.parse('6------6')
        self.assertEqual(len(parse), 1)
        self.assertEqual(parse[0].rule_name, 'missing_pitches')

class TestWord(unittest.TestCase):
    """Tests using `word` as the root node"""

    def test_words(self):
        parser = ParserCantusVolpiano(root='word')
        parse = parser.parser.parse('fgf-ef--fg-h')
        self.assertEqual(len(parse), 3)
        self.assertEqual(parse[0].rule_name, 'syllable')
        self.assertEqual(parse[1].rule_name, 'syllable_boundary')
        self.assertEqual(parse[2].rule_name, 'syllable')

class TestVolpiano(unittest.TestCase):
    """Tests using `volpiano` as the root node"""

    def test_hyphensAtEnd(self):
        parser = ParserCantusVolpiano()
        parse = parser.parse('1---l-')
        self.assertFalse(parse.error)
        parse = parser.parse('1---l--')
        self.assertFalse(parse.error)

    def test_volpiano(self):
        parser = ParserCantusVolpiano(root='volpiano')
        parse = parser.parse('1---fgf-ef--fg-h---f-g')
        word0, bound1, word1, bound2, word2, EOF = parse
        self.assertEqual(word0.rule_name, 'word')
        self.assertEqual(bound1.rule_name, 'word_boundary')
        self.assertEqual(word1.rule_name, 'word')
        self.assertEqual(bound2.rule_name, 'word_boundary')
        self.assertEqual(word2.rule_name, 'word')
        self.assertEqual(EOF.rule_name, 'EOF')

    def test_breaks_before_neume(self):
        parser = ParserCantusVolpiano(root='neume')
        (line_break,), _, _, _ = parser.parser.parse('7fgf')
        self.assertEqual(line_break.rule_name, 'line_break')

    def test_breaks_after_neume(self):
        parser = ParserCantusVolpiano(root='neume')
        _, _, _, (page_break,) = parser.parser.parse('fgf77')
        self.assertEqual(page_break.rule_name, 'page_break')

class TestMissingPitches(unittest.TestCase):

    def test_missing_pitches(self):
        """Are missing pitches correctly parsed?"""
        parser = ParserCantusVolpiano(root='volpiano')
        parse = parser.parser.parse('1---6------6')
        _, _, word, EOF = parse
        self.assertEqual(word.rule_name, 'word')
        self.assertEqual(word[0].rule_name, 'syllable')
        self.assertEqual(word[0][0].rule_name, 'missing_pitches')
        
    def test_missing_pitches_with_break(self):
        """Test whether missing pitches directly followed by a break
        are correctly parsed"""
        parser = ParserCantusVolpiano(root='volpiano')
        parse = parser.parser.parse('1---6------677')
        _, _, word, eof = parse
        missing = word[0][0]
        self.assertEqual(missing.rule_name, 'missing_pitches')
        self.assertEqual(missing[0].value, '6------6')
        self.assertEqual(missing[1].rule_name, 'break')
        
if __name__ == '__main__':
    unittest.main()