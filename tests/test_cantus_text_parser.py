import unittest
from chant21.cantus import ParserCantusText

class TestGrammar(unittest.TestCase):

    def test_basic(self):
        parser = ParserCantusText()
        (words,), EOF = parser.parse('this is a test')
        self.assertEqual(words.rule_name, 'words')
        this, _, word_is, _, a, _, test = words
        self.assertEqual(this.rule_name, 'word')
        self.assertEqual(word_is.rule_name, 'word')
        self.assertEqual(a.rule_name, 'word')
        self.assertEqual(test.rule_name, 'word')

    def test_sections(self):
        parser = ParserCantusText()
        parse = parser.parse('a b | a b c | d')
        section1, bar1, section2, bar2, section3, eof = parse
        self.assertEqual(section1.rule_name, 'section')
        self.assertEqual(bar1.rule_name, 'barline')
        self.assertEqual(section2.rule_name, 'section')
        self.assertEqual(bar2.rule_name, 'barline')
        self.assertEqual(section3.rule_name, 'section')
    
    def test_section_end(self):
        parser = ParserCantusText()
        parse = parser.parse('a b | c |')
        section1, bar1, section2, bar2, eof = parse
        self.assertEqual(section1.rule_name, 'section')
        self.assertEqual(bar1.rule_name, 'barline')
        self.assertEqual(section2.rule_name, 'section')
        self.assertEqual(bar2.rule_name, 'barline')

    def test_psalm_incipit(self):
        parser = ParserCantusText()
        section, eof = parser.parse('~a b')
        self.assertEqual(section[0].rule_name, 'tilda')

    def test_ipsum(self):
        parser = ParserCantusText()
        parse = parser.parse('~Ipsum [c]')
        print(parse)

    def test_incipit(self):
        parser = ParserCantusText()
        parse = parser.parse('b a*')
        print(parse)

    def test_missing_pitches_words(self):
        parser = ParserCantusText()
        section, eof = parser.parse('a b {cde fg}')
        a, _, b, _, missing = section[0]
        self.assertEqual(missing.rule_name, 'missing_pitches')
        self.assertEqual(a.rule_name, 'word')
        self.assertEqual(b.rule_name, 'word')

    def test_missing_pitches_syllables(self):
        parser = ParserCantusText()
        (words,), eof = parser.parse('a b{cd}')
        a, _, b_, missing = words
        # TODO this is not optimal: should be one word
        self.assertEqual(missing.rule_name, 'missing_pitches')

    def test_tilda_text(self):
        # TODO how to convert this? See chant_003353
        text = "Et ab ~parce servo tuo"
        parser = ParserCantusText()
        parse = parser.parse(text)
        words = parse[0][0]
        et, _, ab, _, tilda = words
        self.assertEqual(tilda.rule_name, 'tilda')
    
    # def test_pitchless_text(self):
    #     parser = ParserCantusText()
    #     parse = parser.parse('~A B C')
    #     print(parse)

if __name__ == '__main__':
    unittest.main()