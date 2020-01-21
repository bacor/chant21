import unittest
from volpyano.volpyano_parser import VolpianoParser

class TestSyllable(unittest.TestCase):
    """Tests using `syllable` as the root node"""

    def test_syllables(self):
        parser = VolpianoParser(root='syllable')
        parse = parser.parse('fgf-ef')
        self.assertEqual(len(parse), 3)
        self.assertEqual(parse[0].rule_name, 'neume')
        self.assertEqual(parse[1].rule_name, 'neume_boundary')
        self.assertEqual(parse[2].rule_name, 'neume')

class TestWord(unittest.TestCase):
    """Tests using `word` as the root node"""

    def test_words(self):
        parser = VolpianoParser(root='word')
        parse = parser.parse('fgf-ef--fg-h')
        self.assertEqual(len(parse), 3)
        self.assertEqual(parse[0].rule_name, 'syllable')
        self.assertEqual(parse[1].rule_name, 'syllable_boundary')
        self.assertEqual(parse[2].rule_name, 'syllable')

class TestVolpiano(unittest.TestCase):
    """Tests using `volpiano` as the root node"""

    def test_volpiano(self):
        parser = VolpianoParser(root='volpiano')
        parse = parser.parse('fgf-ef--fg-h---f-g')
        self.assertEqual(len(parse), 4)
        self.assertEqual(parse[0].rule_name, 'word')
        self.assertEqual(parse[1].rule_name, 'word_boundary')
        self.assertEqual(parse[2].rule_name, 'word')
        self.assertEqual(parse[3].rule_name, 'EOF')

if __name__ == '__main__':
    unittest.main()