"""Unittests for the GABC PEG grammar

Author: Bas Cornelissen
Date: 27 December 2019

TODO
    * Test advanced music: code
    * Test advanced music: choral_sign
    * Test advanced music: translation
"""
import unittest
from arpeggio import NoMatch
from chant21 import ParserGABC

class TestFile(unittest.TestCase):
    def test_file(self):
        parser = ParserGABC()
        fileStr = 'attr1:value1;\nattr2:value2;\n%%\n\na(f)b(g) c(h)\ni(j)'
        parse = parser.parse(fileStr)
        self.assertEqual(parse[0].rule_name, 'header')
        self.assertEqual(parse[1].rule_name, 'separator')
        self.assertEqual(parse[2].rule_name, 'body')
        self.assertEqual(parse[3].rule_name, 'EOF')

    def test_emptyHeader(self):
        parser = ParserGABC()
        fileStr = '%%\na(f)b(g)'
        parse = parser.parse(fileStr)
        self.assertEqual(parse[0].rule_name, 'separator')
        self.assertEqual(parse[1].rule_name, 'body')
        self.assertEqual(parse[1].value, 'a | ( | f | ) | b | ( | g | ) | ')
    
    def test_emptyBody(self):
        parser = ParserGABC()
        fileStr = 'attr1:value1;\n%%\n'
        parse = parser.parse(fileStr)
        self.assertEqual(parse[0].rule_name, 'header')
        self.assertEqual(parse[1].rule_name, 'separator')
        self.assertEqual(parse[2].rule_name, 'EOF')

    def test_emptyHeaderAndBody(self):
        parser = ParserGABC()
        fileStr = '%%\n'
        parse = parser.parse(fileStr)
        self.assertEqual(parse[0].value, '%%\n')
        self.assertEqual(parse[1].rule_name, 'EOF')

    def test_bodyConfusedForHeader(self):
        """Tests that the body is not confused for the header when it contains
        both colons and semicolons"""
        parser = ParserGABC(root='file')
        parse = parser.parse('%%\na :(g) (;)')
        self.assertEqual(parse[0].value, '%%\n')
        self.assertEqual(parse[1].rule_name, 'body')
        self.assertEqual(parse[2].rule_name, 'EOF')
    
    def test_multipleHeaders(self):
        parser = ParserGABC()
        fileStr = 'attr1:value1;\n%%\nattr2:value2;\n%%\n(c2) A(f)'
        parse = parser.parse(fileStr)
        h1, sep1, h2, sep2, body, _ = parse
        self.assertEqual(h1.rule_name, 'header')
        self.assertEqual(h1.value, 'attr1 | : | value1 | ;\n')
        self.assertEqual(sep1.rule_name, 'separator')
        self.assertEqual(h2.rule_name, 'header')
        self.assertEqual(h2.value, 'attr2 | : | value2 | ;\n')
        self.assertEqual(sep2.rule_name, 'separator')
        self.assertEqual(body.rule_name, 'body')

class TestHeader(unittest.TestCase):

    def test_header(self):
        parser = ParserGABC(root='header')
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

    def test_bracketsSpaces(self):
        parser = ParserGABC(root='header')
        headerStr = "attr1:value1 (test);"
        parse = parser.parse(headerStr)
        self.assertFalse(parse.error)

    def test_semicolons(self):
        parser = ParserGABC(root='header')
        headerStr = "attr1:value1; value2;"
        parse = parser.parse(headerStr)
        self.assertEqual(parse[0][2].value, 'value1; value2')
        # TODO test raises error when not followed by space

class TestBody(unittest.TestCase):
    def test_body(self):
        parser = ParserGABC(root='body')
        parse = parser.parse('A(f)B(g) C(h)')
        self.assertEqual(parse.rule_name, 'body')
        self.assertEqual(parse[0].rule_name, 'word')
        self.assertEqual(parse[0].value, 'A | ( | f | ) | B | ( | g | )')
        self.assertEqual(parse[1].rule_name, 'whitespace')
        self.assertEqual(parse[2].rule_name, 'word')
        self.assertEqual(parse[2].value, 'C | ( | h | )')

    def test_otherWhitespace(self):
        parser = ParserGABC(root='body')
        spaces = [' ', '\n', '\t', '\f', '\v', '\r', '  ', '\n   \t']
        for space in spaces:
            parse = parser.parse('A(f)' + space)
            self.assertEqual(parse[0].rule_name, 'word')
            self.assertEqual(parse[0].value, 'A | ( | f | )')
            self.assertEqual(parse[1].rule_name, 'whitespace')
            self.assertEqual(parse[1].value, space)

    def test_wordsWithSpaces(self):
        parser = ParserGABC(root='body')
        parse = parser.parse('A(f)B (g) C(h)')
        self.assertEqual(parse[0].rule_name, 'word')
        self.assertEqual(parse[0].value, 'A | ( | f | ) | B  | ( | g | )')
        self.assertEqual(parse[1].rule_name, 'whitespace')
        self.assertEqual(parse[2].rule_name, 'word')
        self.assertEqual(parse[2].value, 'C | ( | h | )')

    def test_wordWithSpaceAndBarlines(self):
        parser = ParserGABC(root='body')
        parse = parser.parse('a(f)b (g) (:)')
        self.assertEqual(parse[0].rule_name, 'word')
        self.assertEqual(parse[1].rule_name, 'whitespace')
        self.assertEqual(parse[2].rule_name, 'not_music')
        self.assertEqual(parse[2].value, '( | : | )')

class TestWord(unittest.TestCase):
    def test_word(self):
        parser = ParserGABC(root='word')
        parse = parser.parse('A(f)B(g)')

        self.assertEqual(parse.rule_name, 'word')
        # First syllable
        self.assertEqual(parse[0].rule_name, 'syllable')
        self.assertEqual(parse[0].value, 'A | ( | f | )')
        # second syllable
        self.assertEqual(parse[1].rule_name, 'syllable')
        self.assertEqual(parse[1].value, 'B | ( | g | )')

    def test_wordWithSpaces(self):
        parser = ParserGABC(root='word')
        parse = parser.parse('A (f)B(g)')
        self.assertEqual(parse.rule_name, 'word')
        self.assertEqual(parse[0].rule_name, 'syllable')
        self.assertEqual(parse[0].value, 'A  | ( | f | )')

    # def test_barline(self):
    #     parser = ParserGABC(root='word')
    #     self.assertRaises(NoMatch, lambda: parser.parse('(:)'))

class TestNotMusic(unittest.TestCase):
    def test_clef(self):
        parser = ParserGABC(root='not_music')
        parse = parser.parse('(c3)')
        self.assertEqual(parse[0].value, '(')
        self.assertEqual(parse[1].rule_name, 'clef')
        self.assertEqual(parse[2].value, ')')

    def test_clefTypes(self):
        parser = ParserGABC(root='clef')
        clefs = 'c1 c2 c3 c4 f1 f2 f3 f4 cb3'.split()
        for clef_str in clefs:
            parse = parser.parse(clef_str)
            self.assertEqual(parse.rule_name, 'clef')
            self.assertEqual(parse.value, clef_str)

    def test_clefChange(self):
        # http://gregorio-project.github.io/gabc/details.html#endofline
        parser = ParserGABC(root='not_music')
        parse = parser.parse('(z::c3)')
        _, lineEnd, bar, clef, _ = parse
        self.assertEqual(lineEnd.rule_name, 'end_of_line')
        self.assertEqual(bar.rule_name, 'pausa')
        self.assertEqual(clef.rule_name, 'clef')

        gabc = "<sp>V/</sp>.(z0::c3)"
        parse = parser.parse(gabc)
        text, _, lineEnd, bar, clef, _ = parse
        self.assertEqual(text.value, '<sp>V/</sp>.')
        self.assertEqual(text.rule_name, 'text')
        self.assertEqual(lineEnd.rule_name, 'end_of_line')
        self.assertEqual(bar.rule_name, 'pausa')
        self.assertEqual(clef.rule_name, 'clef')

    def test_clefsFollowedByMusic(self):
        parser = ParserGABC(root='body')
        parse = parser.parse('(c4)a(fg)')
        clef, word, _ = parse
        self.assertEqual(clef.rule_name, 'not_music')
        self.assertEqual(word.rule_name, 'word')

    def test_barline(self):
        parser = ParserGABC(root='not_music')
        parse = parser.parse(':*(:)')
        self.assertEqual(parse[0].rule_name, 'text')
        self.assertEqual(parse[0].value, ':*')
        self.assertEqual(parse[1].value, '(')
        self.assertEqual(parse[2].rule_name, 'pausa')
        self.assertEqual(parse[2].value, ':')
        self.assertEqual(parse[3].value, ')')

        parse = parser.parse('(::)')
        self.assertEqual(parse[0].value, '(')
        self.assertEqual(parse[1].rule_name, 'pausa')
        self.assertEqual(parse[1].value, '::')
        self.assertEqual(parse[2].value, ')')

    def test_barlinesAndCommas(self):
        parser = ParserGABC(root='body')
        parse = parser.parse('a(:) b(f) (,) (g) (::)')
        bar1, _, word, _, bar2, _ = parse
        self.assertEqual(bar1.rule_name, 'not_music')
        self.assertEqual(bar1.value, 'a | ( | : | )')
        self.assertEqual(word.rule_name, 'word')
        self.assertEqual(len(word), 1)
        self.assertEqual(word[0].rule_name, 'syllable')
        self.assertEqual(bar2.rule_name, 'not_music')
        self.assertEqual(bar2.value, '( | :: | )')
    
    def test_barlinesFollowedByText(self):
        parser = ParserGABC(root='body')
        parse = parser.parse('(:)a()')
        self.assertEqual(len(parse), 3)
        bar, textEl, _ = parse 
        self.assertEqual(parse[0].rule_name, 'not_music')
        self.assertEqual(parse[1].rule_name, 'not_music')

    def test_barlineDirectlyAfterMusic(self):
        parser = ParserGABC(root='body')

        # The normal situation, with space:
        parse = parser.parse('A(f) (:)')
        word, _, bar, _ = parse
        self.assertEqual(word.rule_name, 'word')
        self.assertEqual(bar.rule_name, 'not_music')

        # The weird situation, without space:
        parse = parser.parse('A(f)(:)')
        syll1, syll2 = parse[0]
        self.assertEqual(syll1.rule_name, 'syllable')
        self.assertEqual(syll1.value, 'A | ( | f | )')
        self.assertEqual(syll2.rule_name, 'syllable')
        self.assertEqual(syll2[1][0].rule_name, 'pausa_in_music')

    def test_custos(self):
        parser = ParserGABC(root='not_music')
        parse = parser.parse('(::i+)')
        _, bar, custos, _ = parse
        self.assertEqual(custos.rule_name, 'custos')
        self.assertEqual(custos.value, 'i+')
    
    def test_emptyCustos(self):
        """Custos without position, makes no sense, but included anyway"""
        parser = ParserGABC(root='not_music')
        parse = parser.parse('(::+)')
        _, bar, custos, _ = parse
        self.assertEqual(custos.rule_name, 'custos')
        self.assertEqual(custos.value, '+')

class TestSyllable(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestSyllable, self).__init__(*args, **kwargs)
        self.parser = ParserGABC(root='syllable')

    def test_textMusic(self):
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

    def test_spaces(self):
        """Test whether a syllable starting with a space does not match"""
        self.assertRaises(NoMatch, lambda: self.parser.parse(' a(f)'))

    def test_spacesInMusic(self):
        parser = ParserGABC(root='music')
        parse = parser.parse('f , g')
        n1, sp1, comma, sp2, n2 = parse
        self.assertEqual(sp1.rule_name, 'spacer')
        self.assertEqual(comma.rule_name, 'pausa_in_music')
        self.assertEqual(comma.value, ',')
        self.assertEqual(sp2.rule_name, 'spacer')

    def test_comma(self):
        parser = ParserGABC(root='syllable')
        comma_examples = [
            '(f)(,)(g)',
            '(f)(;)(g)',
            '(f,g)',
            '(f;g)',
            '(f) (,) (g)',
            '(f) (;) (g)'
        ]
        for gabc in comma_examples:
            parse = parser.parse(gabc)
            n1, comma, n2 = parse[1]
            self.assertEqual(n1.rule_name, 'note')
            self.assertEqual(n1.value, 'f')
            self.assertEqual(comma.rule_name, 'pausa_in_music')
            self.assertEqual(n2.rule_name, 'note')
            self.assertEqual(n2.value, 'g')

    def test_commaInBody(self):
        parser = ParserGABC(root='body')
        parse = parser.parse('(f) (,) (g)')
        self.assertEqual(len(parse), 2)
        self.assertEqual(parse[0].rule_name, 'word')
        self.assertEqual(len(parse[0]), 1)

        parse = parser.parse('(f) (,) A(g)')
        word1, _, comma, _, word2, _ = parse
        self.assertEqual(word1.rule_name, 'word')
        self.assertEqual(word1.value, '( | f | )')
        self.assertEqual(comma.rule_name, 'not_music')
        self.assertEqual(comma.value, '( | , | )')
        self.assertEqual(word2.rule_name, 'word')
        self.assertEqual(word2.value, 'A | ( | g | )')

    def test_pausaMinorInMusic(self):
        """A pausa minor is allowed in the music if surrounded by spaces"""
        parser = ParserGABC(root='music')
        parse = parser.parse('f,g ; f')
        n1, c1, n2, _, c2, _, n3 = parse
        self.assertEqual(c1.rule_name, 'pausa_in_music')
        self.assertEqual(c1.value, ',')
        self.assertEqual(c2.rule_name, 'pausa_in_music')
        self.assertEqual(c2.value, ';')

    def test_pausaMinorInBody(self):
        parser = ParserGABC(root='body')
        parse = parser.parse('(f;f) (;)')
        print(parse)
        # TODO fix this: how to deal with comma's
        # and pausa minima etc within melismas.
        # Perhaps the quesiton is whether we want pausa min
        # to end a measure in music21. If not; treat
        # them as comma's.

    def test_tags(self):
        parse = self.parser.parse('<i>test</i>(f)')
        self.assertEqual(parse[0].rule_name, 'text')
        self.assertEqual(parse[0].value, '<i>test</i>')

class TestAdvanced(unittest.TestCase):
    
    def test_accidental(self):
        parser = ParserGABC(root='music')
        parse = parser.parse('fxgwf')
        self.assertEqual(len(parse), 3)
        self.assertEqual(parse[0].rule_name, 'alteration')
        self.assertEqual(parse[1].rule_name, 'note')
        self.assertEqual(parse[2].rule_name, 'note')

    def test_polyphony(self):
        gabc = '{i}'
        parser = ParserGABC(root='music')
        parse = parser.parse(gabc)
        self.assertEqual(parse[0].rule_name, 'advanced')
        self.assertEqual(parse[0][0].rule_name, 'polyphony')

    def test_braces(self):
        braces = [
            '[ob:1]',
            '[ob:1;6mm]',
            '[ocb:1;18mm]',
            '[ocb:1;18.1235mm]',
            '[ocba:1{]',
            '[ocba:0}]',
        ]
        parser = ParserGABC(root='music')
        for gabc in braces: 
            parse = parser.parse(gabc)
            self.assertEqual(parse[0].rule_name, 'advanced')
            self.assertEqual(parse[0][0].rule_name, 'brace')
            self.assertEqual(parse[0][0].value, gabc)

    def test_verbatimCode(self):
        parser = ParserGABC(root='code')
        codeExamples = [
            '[nv:\mycode]', 
            '[gv:\mycode]', 
            '[ev:\mycode]', 
        ]
        for code in codeExamples:
            parse = parser.parse(code)
            self.assertEqual(parse.rule_name, 'code')
            self.assertEqual(parse[1].rule_name, 'verbatim_code')
    
    def test_macroReferences(self):
        parser = ParserGABC(root='code')
        codeExamples = ['[nm1]', '[gm1]', '[em1]']
        for code in codeExamples:
            parse = parser.parse(code)
            self.assertEqual(parse.rule_name, 'code')
            self.assertEqual(parse[1].rule_name, 'macro_reference')

    def test_macroAboveBody(self):
        parser = ParserGABC(root='body')
        parse = parser.parse('(c2) def-m1:\grealign;\ndef-m2:\grealign;\na(f)')
        clef, _, macro1, _, macro2, _, word, _ = parse
        self.assertEqual(macro1.rule_name, 'macro')
        self.assertEqual(macro2.rule_name, 'macro')
        self.assertEqual(clef.rule_name, 'not_music')
        self.assertEqual(word.rule_name, 'word')

class TestNote(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestNote, self).__init__(*args, **kwargs)
        self.parser = ParserGABC(root='note')
        
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

    def test_emptyNotes(self):
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

    def test_rhythmicSigns(self):
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

    def test_oneNoteNeumes(self):
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

class TestAlterations(unittest.TestCase):
    
    def test_alteration(self):
        parser = ParserGABC(root='alteration')
        parse = parser.parse('gx')
        self.assertEqual(parse.rule_name, 'alteration')
        self.assertEqual(parse[0].rule_name, 'position')
        self.assertEqual(parse[1].value, 'x')

        parse = parser.parse('gy')
        self.assertEqual(parse.rule_name, 'alteration')
        self.assertEqual(parse[1].value, 'y')

        parse = parser.parse('g#')
        self.assertEqual(parse.rule_name, 'alteration')
        self.assertEqual(parse[1].value, '#')

    def test_alterationSuffixes(self):
        """Test suffixes on accidentals, which make no sense but sometimes occur"""
        gabc = "ix~fgfg"
        parser = ParserGABC(root='music')
        parse = parser.parse(gabc)
        self.assertEqual(parse.value, 'i | x | ~ | f | g | f | g')
    
    def test_polyphonicAlterations(self):
        parser = ParserGABC(root='music')
        parse = parser.parse('f{ix}g')
        n1, advanced, n2 = parse
        self.assertEqual(len(advanced), 1)
        self.assertEqual(advanced[0].rule_name, 'polyphony')
        self.assertEqual(advanced[0][1].rule_name, 'alteration')

if __name__  ==  '__main__':
    unittest.main()