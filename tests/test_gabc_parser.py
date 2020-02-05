import unittest
from chant21 import ParserGABC

class TestParserGABC(unittest.TestCase):

    def test_invalidArguments(self):
        func = lambda: ParserGABC(grammar_path='foo')
        self.assertRaises(Exception, func)

        func = lambda: ParserGABC(root='gabc_faile')
        self.assertRaises(Exception, func)

    def test_parseString(self):
        parser = ParserGABC()
        fileStr = 'attr1:value1;\nattr2:value2;%%\n\na(f)b(g) c(h)\ni(j)'
        parse = parser.parse(fileStr)

        # These tests are identical to TestFile.test_file in `peg_test.py`
        # Header
        self.assertEqual(parse[0].rule_name, 'header')
        self.assertEqual(parse[0].value, 'attr1 | : | value1 | ;\n | attr2 | : | value2 | ;')
        # Head/body separator
        self.assertEqual(parse[1].value, '%%\n\n')
        # Body
        self.assertEqual(parse[2].rule_name, 'body')
        self.assertEqual(parse[2].value, 'a | ( | f | ) | b | ( | g | ) |   | c | ( | h | ) | \n | i | ( | j | ) | ')

    def test_parseFile(self):
        parser = ParserGABC()
        parse = parser.parseFile('chant21/examples/minimal.gabc')
        self.assertEqual(parse[0].value, 'attribute | : | value | ;\n')
        self.assertEqual(parse[1].value, '%%\n')
        self.assertEqual(parse[2].value, 'A | ( | f | ) | B | ( | g | ) |   | C | ( | h | ) | ')
        self.assertEqual(parse[3].rule_name, 'EOF')

if __name__ == '__main__':
    unittest.main()