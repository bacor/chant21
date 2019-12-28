"""Unittests for the GABC PEG grammar

Author: Bas Cornelissen
Date: 27 December 2019
"""
import unittest
from arpeggio import NoMatch
from pygabc.parser import GABCParser

class TestFile(unittest.TestCase):
    def test_file(self):
        parser = GABCParser()
        file_str = 'attr1:value1;\nattr2:value2;%%\n\na(f)b(g) c(h)\ni(j)'
        parse = parser.parse(file_str)
        # Header
        self.assertEqual(parse[0].rule_name, 'header')
        self.assertEqual(parse[0].value, 'attr1 | : | value1 | ;\n | attr2 | : | value2 | ;')
        # Head/body separator
        self.assertEqual(parse[1].value, '%%\n\n')
        # Body
        self.assertEqual(parse[2].rule_name, 'body')
        self.assertEqual(parse[2].value, 'a | ( | f | ) | b | ( | g | ) |   | c | ( | h | ) | \n | i | ( | j | ) | ')

    def test_empty_header(self):
        parser = GABCParser()
        file_str = '%%\na(f)b(g)'
        parse = parser.parse(file_str)
        
        self.assertNotEqual(parse[0].rule_name, 'header')
        self.assertEqual(parse[0].value, '%%\n')
        self.assertEqual(parse[1].value, 'a | ( | f | ) | b | ( | g | ) | ')
    
    def test_empty_body(self):
        parser = GABCParser()
        file_str = 'attr1:value1;\n%%\n'
        parse = parser.parse(file_str)

        self.assertEqual(parse[0].rule_name, 'header')
        self.assertEqual(parse[0].value, 'attr1 | : | value1 | ;\n')
        self.assertEqual(parse[1].value, '%%\n')
        self.assertEqual(parse[2].rule_name, 'EOF')

    def test_empty_header_and_body(self):
        parser = GABCParser()
        file_str = '%%\n'
        parse = parser.parse(file_str)
        self.assertEqual(parse[0].value, '%%\n')
        self.assertEqual(parse[1].rule_name, 'EOF')

    def test_body_confused_for_header(self):
        """Tests that the body is not confused for the header when it contains
        both colons and semicolons"""
        parser = GABCParser(root='gabc_file')
        parse = parser.parse('%%\na :(g) (;)')
        self.assertEqual(parse[0].value, '%%\n')
        self.assertEqual(parse[1].rule_name, 'body')
        self.assertEqual(parse[2].rule_name, 'EOF')

class TestHeader(unittest.TestCase):

    def test_header(self):
        parser = GABCParser(root='header')
        header_str = "attr1: value1;\n\nattr2:value2;"
        parse = parser.parse(header_str)
        
        # Attribute 1
        attr1 = parse[0]
        self.assertEqual(attr1.rule_name, 'attribute')
        # Key
        self.assertEqual(attr1[0].rule_name, 'attribute_key')
        self.assertEqual(attr1[0].value, 'attr1')
        # Separator: colon
        self.assertEqual(attr1[1].value, ': ')
        # Value
        self.assertEqual(attr1[2].rule_name, 'attribute_value')
        self.assertEqual(attr1[2].value, 'value1')
        # Attribute end
        self.assertEqual(attr1[3].value, ';\n\n')

        # Attribute 2
        attr2 = parse[1]
        self.assertEqual(attr2.rule_name, 'attribute')
        # Key
        self.assertEqual(attr2[0].rule_name, 'attribute_key')
        self.assertEqual(attr2[0].value, 'attr2')
        # Separator: colon
        self.assertEqual(attr2[1].value, ':')
        # Value
        self.assertEqual(attr2[2].rule_name, 'attribute_value')
        self.assertEqual(attr2[2].value, 'value2')
        # Attribute end
        self.assertEqual(attr2[3].value, ';')

    def test_brackets_spaces(self):
        parser = GABCParser(root='header')
        header_str = "attr1:value1 (test);"
        parse = parser.parse(header_str)
        self.assertFalse(parse.error)

class TestBody(unittest.TestCase):
    def test_body(self):
        parser = GABCParser(root='body')
        parse = parser.parse('A(f)B(g) C(h)')
        self.assertEqual(parse.rule_name, 'body')
        self.assertEqual(parse[0].rule_name, 'word')
        self.assertEqual(parse[0].value, 'A | ( | f | ) | B | ( | g | )')
        self.assertEqual(parse[1].rule_name, 'whitespace')
        self.assertEqual(parse[2].rule_name, 'word')
        self.assertEqual(parse[2].value, 'C | ( | h | )')

    def test_other_whitespace(self):
        parser = GABCParser(root='body')
        spaces = [' ', '\n', '\t', '\f', '\v', '\r', '  ', '\n   \t']
        for space in spaces:
            parse = parser.parse('A(f)' + space)
            self.assertEqual(parse[0].rule_name, 'word')
            self.assertEqual(parse[0].value, 'A | ( | f | )')
            self.assertEqual(parse[1].rule_name, 'whitespace')
            self.assertEqual(parse[1].value, space)

    def test_words_with_spaces(self):
        parser = GABCParser(root='body')
        parse = parser.parse('A(f)B (g) C(h)')
        self.assertEqual(parse[0].rule_name, 'word')
        self.assertEqual(parse[0].value, 'A | ( | f | ) | B  | ( | g | )')
        self.assertEqual(parse[1].rule_name, 'whitespace')
        self.assertEqual(parse[2].rule_name, 'word')
        self.assertEqual(parse[2].value, 'C | ( | h | )')

    def test_word_with_space_and_barlines(self):
        parser = GABCParser(root='body')
        parse = parser.parse('a(f)b (g) (;)')
        self.assertEqual(parse[0].rule_name, 'word')
        self.assertEqual(parse[1].rule_name, 'whitespace')
        self.assertEqual(parse[2].rule_name, 'word')
        self.assertEqual(parse[2].value, '( | ; | )')

class TestWord(unittest.TestCase):
    def test_word(self):
        parser = GABCParser(root='word')
        parse = parser.parse('A(f)B(g)')

        self.assertEqual(parse.rule_name, 'word')
        # First syllable
        self.assertEqual(parse[0].rule_name, 'syllable')
        self.assertEqual(parse[0].value, 'A | ( | f | )')
        # second syllable
        self.assertEqual(parse[1].rule_name, 'syllable')
        self.assertEqual(parse[1].value, 'B | ( | g | )')

    def test_word_with_spaces(self):
        parser = GABCParser(root='word')
        parse = parser.parse('A (f)B(g)')
        self.assertEqual(parse.rule_name, 'word')
        self.assertEqual(parse[0].rule_name, 'syllable')
        self.assertEqual(parse[0].value, 'A  | ( | f | )')

    def test_barline(self):
        parser = GABCParser(root='word')
        parse = parser.parse('(;)')
        self.assertEqual(parse.rule_name, 'word')
        self.assertEqual(parse.value, '( | ; | )')

class TestSyllable(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestSyllable, self).__init__(*args, **kwargs)
        self.parser = GABCParser(root='syllable')

    def test_clef(self):
        parse = self.parser.parse('(c3)')
        self.assertEqual(parse[0].value, '(')
        self.assertEqual(parse[1].rule_name, 'music')
        self.assertEqual(parse[2].value, ')')

        self.assertEqual(parse[1][0].rule_name, 'clef')
        self.assertEqual(parse[1][0].value, 'c3')

    def test_text_music(self):
        parse = self.parser.parse('a_string(fgf)')

        self.assertEqual(parse.rule_name, 'syllable')
        self.assertEqual(parse[0].rule_name, 'text')
        self.assertEqual(parse[0].value, 'a_string')
        self.assertEqual(parse[1].value, '(')
        self.assertEqual(parse[2].rule_name, 'music')
        self.assertEqual(parse[3].value, ')')
    
        self.assertEqual(parse[2][0].rule_name, 'note')
        self.assertEqual(parse[2][1].rule_name, 'note')
        self.assertEqual(parse[2][2].rule_name, 'note')

        self.assertEqual(parse[2][0][0].rule_name, 'position')
        self.assertEqual(parse[2][0][0].value, 'f')

    def test_barline(self):
        parse = self.parser.parse(':*(:)')

        self.assertEqual(parse[0].rule_name, 'text')
        self.assertEqual(parse[0].value, ':*')
        self.assertEqual(parse[1].value, '(')
        self.assertEqual(parse[2].rule_name, 'music')
        self.assertEqual(parse[3].value, ')')

        self.assertEqual(parse[2][0].rule_name, 'barline')
        self.assertEqual(parse[2][0].value, ':')

    def test_barline_2(self):
        parse = self.parser.parse('(::)')

        self.assertEqual(parse[0].value, '(')
        self.assertEqual(parse[1].rule_name, 'music')
        self.assertEqual(parse[2].value, ')')

        self.assertEqual(parse[1][0].rule_name, 'barline')
        self.assertEqual(parse[1][0].value, '::')

    def test_spaces(self):
        """Test whether a syllable starting with a space does not match"""
        self.assertRaises(NoMatch, lambda: self.parser.parse(' a(f)'))

    def test_spaces_in_music(self):
        parse = self.parser.parse('(f , g)')
        self.assertEqual(parse[1][1].rule_name, 'spacer')
        self.assertEqual(parse[1][2].rule_name, 'barline')
        self.assertEqual(parse[1][2].value, ',')
        self.assertEqual(parse[1][3].rule_name, 'spacer')

class TestClef(unittest.TestCase):

    def test_clefs(self):
        parser = GABCParser(root='clef')
        clefs = 'c1 c2 c3 c4 f1 f2 f3 f4 cb3'.split()
        for clef_str in clefs:
            parse = parser.parse(clef_str)
            self.assertEqual(parse.rule_name, 'clef')
            self.assertEqual(parse.value, clef_str)

class TestNote(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestNote, self).__init__(*args, **kwargs)
        self.parser = GABCParser(root='note')
        
    def test_positions(self):
        for position in 'abcdefghijklm':
            parse = self.parser.parse(position)
            self.assertEqual(parse.rule_name, 'note')
            self.assertEqual(parse[0].rule_name, 'position')
            self.assertEqual(parse[0].value, position)

    def test_accents(self):
        parse = self.parser.parse('gr1')

        self.assertEqual(parse[0].rule_name, 'position')
        self.assertEqual(parse[0].value, 'g')
        self.assertEqual(parse[1].rule_name, 'suffix')
        self.assertEqual(parse[1].value, 'r1')
        self.assertEqual(parse[1][0].rule_name, 'empty_note_or_accent')

        parse = self.parser.parse("gr2")
        self.assertEqual(parse[1].value, "r2")
        self.assertEqual(parse[1][0].rule_name, 'empty_note_or_accent')

        parse = self.parser.parse("gr3")
        self.assertEqual(parse[1].value, "r3")
        self.assertEqual(parse[1][0].rule_name, 'empty_note_or_accent')

        parse = self.parser.parse("gr4")
        self.assertEqual(parse[1].value, "r4")
        self.assertEqual(parse[1][0].rule_name, 'empty_note_or_accent')

        parse = self.parser.parse("gr5")
        self.assertEqual(parse[1].value, "r5")
        self.assertEqual(parse[1][0].rule_name, 'empty_note_or_accent')

        # Multiple 
        parse = self.parser.parse("gr0r3")
        self.assertEqual(parse[1].rule_name, 'suffix')
        self.assertEqual(parse[1][0].rule_name, 'empty_note_or_accent')
        self.assertEqual(parse[1][0].value, "r0")
        self.assertEqual(parse[1][0].rule_name, 'empty_note_or_accent')
        self.assertEqual(parse[1][1].value, "r3")
        self.assertEqual(parse[1][1].rule_name, 'empty_note_or_accent')

    def test_empty_notes(self):
        parse = self.parser.parse('gr')
        self.assertEqual(parse[0].rule_name, 'position')
        self.assertEqual(parse[0].value, 'g')
        self.assertEqual(parse[1].rule_name, 'suffix')
        self.assertEqual(parse[1].value, 'r')
        self.assertEqual(parse[1][0].rule_name, 'empty_note_or_accent')

        parse = self.parser.parse("gR")
        self.assertEqual(parse[1].value, "R")
        self.assertEqual(parse[1][0].rule_name, 'empty_note_or_accent')

        parse = self.parser.parse("gr0")
        self.assertEqual(parse[1].value, "r0")
        self.assertEqual(parse[1][0].rule_name, 'empty_note_or_accent')

    def test_rhythmic_signs(self):
        parse = self.parser.parse('g_')
        self.assertEqual(parse[0].rule_name, 'position')
        self.assertEqual(parse[0].value, 'g')
        self.assertEqual(parse[1].rule_name, 'suffix')
        self.assertEqual(parse[1].value, '_')
        self.assertEqual(parse[1][0].rule_name, 'rhythmic_sign')

        parse = self.parser.parse('g..')
        self.assertEqual(parse[1].value, '..')
        self.assertEqual(parse[1][0].rule_name, 'rhythmic_sign')

        parse = self.parser.parse('g..')
        self.assertEqual(parse[1].value, '..')
        self.assertEqual(parse[1][0].rule_name, 'rhythmic_sign')

        parse = self.parser.parse("g'")
        self.assertEqual(parse[1].value, "'")
        self.assertEqual(parse[1][0].rule_name, 'rhythmic_sign')

        parse = self.parser.parse("g'1")
        self.assertEqual(parse[1].value, "'1")
        self.assertEqual(parse[1][0].rule_name, 'rhythmic_sign')

        parse = self.parser.parse('H_502')
        self.assertEqual(parse[0].rule_name, 'position')
        self.assertEqual(parse[0].value, 'H')
        self.assertEqual(parse[1].rule_name, 'suffix')
        self.assertEqual(parse[1].value, '_502')

    def test_one_note_neumes(self):
        # Test single suffix
        parse = self.parser.parse('G~')
        self.assertEqual(parse[0].rule_name, 'position')
        self.assertEqual(parse[0].value, 'G')
        self.assertEqual(parse[1].rule_name, 'suffix')
        self.assertEqual(parse[1].value, '~')
        self.assertEqual(parse[1][0].rule_name, 'neume_shape')

        # Test two-character suffix
        parse = self.parser.parse('Go~')
        self.assertEqual(parse[0].rule_name, 'position')
        self.assertEqual(parse[0].value, 'G')
        self.assertEqual(parse[1].rule_name, 'suffix')
        self.assertEqual(parse[1].value, 'o~')
        self.assertEqual(parse[1][0].rule_name, 'neume_shape')

        # Test all possible suffixes
        # G~ G> g~ g< g> go g~ go< gw gv gV gs gs<
        tests = [('G~', 'G', '~'), ('G>', 'G', '>'), ('g~', 'g', '~'), 
                 ('g<', 'g', '<'), ('g>', 'g', '>'), ('go', 'g', 'o'), 
                 ('g~', 'g', '~'), ('go<', 'g', 'o<'), ('gw', 'g', 'w'),
                 ('gv', 'g', 'v'), ('gV', 'g', 'V'), ('gs', 'g', 's'),
                 ('gs<', 'g', 's<')]
        for string, position, suffix in tests:
            parse = self.parser.parse(string)
            self.assertEqual(parse[0].rule_name, 'position')
            self.assertEqual(parse[0].value, position)
            self.assertEqual(parse[1].value, suffix)
            self.assertEqual(parse[1][0].rule_name, 'neume_shape')

    def test_alterations(self):
        parse = self.parser.parse('gx')
        self.assertEqual(parse[0].rule_name, 'position')
        self.assertEqual(parse[0].value, 'g')
        self.assertEqual(parse[1].rule_name, 'suffix')
        self.assertEqual(parse[1].value, 'x')
        self.assertEqual(parse[1][0].rule_name, 'alteration')

        parse = self.parser.parse('gy')
        self.assertEqual(parse[1].value, 'y')
        self.assertEqual(parse[1][0].rule_name, 'alteration')

        parse = self.parser.parse('g#')
        self.assertEqual(parse[1].value, '#')
        self.assertEqual(parse[1][0].rule_name, 'alteration')

if __name__  ==  '__main__':
    unittest.main()